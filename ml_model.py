"""
ml_model.py
-----------
Handles all ML operations:
  - Category prediction  (TF-IDF + Random Forest)
  - Anomaly detection    (Isolation Forest)
  - Expense forecasting  (Linear Regression)
  - Smart insights       (rule-based + statistics)
"""

import os
import joblib
import numpy as np
import pandas as pd

MODEL_DIR  = MODEL_DIR  = os.path.dirname(__file__)
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")

# ─── Lazy-load the trained model bundle ────────────────────────────────────

_model_bundle = None


def _load_model():
    global _model_bundle
    if _model_bundle is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                "Model not found. Run  python training/train_model.py  first."
            )
        _model_bundle = joblib.load(MODEL_PATH)
    return _model_bundle


# ─── Category prediction ────────────────────────────────────────────────────

def predict_category(description: str) -> dict:
    """
    Given a raw expense description return predicted category + confidence.

    Returns
    -------
    {
        "category": str,
        "confidence": float   # 0-100 percentage
    }
    """
    bundle = _load_model()
    vectorizer: object = bundle["vectorizer"]
    classifier: object = bundle["classifier"]
    labels: list       = bundle["labels"]

    X     = vectorizer.transform([description.lower().strip()])
    proba = classifier.predict_proba(X)[0]
    idx   = int(np.argmax(proba))

    return {
        "category":   labels[idx],
        "confidence": round(float(proba[idx]) * 100, 1),
    }


# ─── Anomaly detection ──────────────────────────────────────────────────────

def detect_anomaly(amount: float, category: str, all_expenses: list) -> bool:
    """
    Detect whether a given expense amount is unusual for its category.
    Uses per-category mean + 2 standard deviations as threshold.
    Falls back to global stats if category has < 3 samples.

    Returns True if the expense is anomalous.
    """
    if not all_expenses:
        return False

    df = pd.DataFrame(all_expenses)

    cat_data = df[df["category"] == category]["amount"]

    if len(cat_data) >= 3:
        mean = cat_data.mean()
        std  = cat_data.std()
    else:
        mean = df["amount"].mean()
        std  = df["amount"].std()

    if std == 0 or np.isnan(std):
        return False

    z_score = (amount - mean) / std
    return abs(z_score) > 2.0


# ─── Expense forecasting ────────────────────────────────────────────────────

def forecast_next_month(monthly_totals: list) -> dict:
    """
    Predict next month's total expense using Linear Regression on monthly data.

    Parameters
    ----------
    monthly_totals : list of {"month": "YYYY-MM", "total": float}

    Returns
    -------
    {
        "predicted_amount": float,
        "trend": "increasing" | "decreasing" | "stable",
        "data_points": int
    }
    """
    if len(monthly_totals) < 2:
        return {
            "predicted_amount": 0.0,
            "trend":            "insufficient_data",
            "data_points":      len(monthly_totals),
        }

    from sklearn.linear_model import LinearRegression

    df = pd.DataFrame(monthly_totals)
    df["x"] = range(len(df))
    X = df[["x"]].values
    y = df["total"].values

    reg = LinearRegression()
    reg.fit(X, y)

    next_x    = np.array([[len(df)]])
    predicted = float(reg.predict(next_x)[0])
    predicted = max(predicted, 0.0)          # never negative

    coef = float(reg.coef_[0])
    if coef > 50:
        trend = "increasing"
    elif coef < -50:
        trend = "decreasing"
    else:
        trend = "stable"

    return {
        "predicted_amount": round(predicted, 2),
        "trend":            trend,
        "data_points":      len(df),
    }


# ─── Smart insights ─────────────────────────────────────────────────────────

def generate_insights(all_expenses: list) -> list:
    """
    Generate human-readable smart insights from expense history.

    Returns a list of insight strings.
    """
    if not all_expenses:
        return ["No expenses recorded yet. Start adding expenses to see insights!"]

    df = pd.DataFrame(all_expenses)
    df["date"]  = pd.to_datetime(df["date"])
    df["month"] = df["date"].dt.to_period("M")

    insights = []
    months   = df["month"].unique()

    if len(months) < 2:
        # Only one month of data
        top_cat = df.groupby("category")["amount"].sum().idxmax()
        top_amt = df.groupby("category")["amount"].sum().max()
        insights.append(f"💸 Your highest spending this month is on {top_cat} (₹{top_amt:,.0f}).")
        total = df["amount"].sum()
        insights.append(f"📊 Total spending so far: ₹{total:,.0f}.")
        return insights

    # Compare last two months
    months_sorted   = sorted(months)
    current_month   = months_sorted[-1]
    previous_month  = months_sorted[-2]

    curr_total = df[df["month"] == current_month]["amount"].sum()
    prev_total = df[df["month"] == previous_month]["amount"].sum()

    if prev_total > 0:
        change_pct = ((curr_total - prev_total) / prev_total) * 100
        direction  = "more" if change_pct > 0 else "less"
        insights.append(
            f"📈 You spent {abs(change_pct):.1f}% {direction} this month "
            f"(₹{curr_total:,.0f}) vs last month (₹{prev_total:,.0f})."
        )

    # Category-level comparison
    curr_cat = df[df["month"] == current_month].groupby("category")["amount"].sum()
    prev_cat = df[df["month"] == previous_month].groupby("category")["amount"].sum()

    for cat in curr_cat.index:
        if cat in prev_cat.index and prev_cat[cat] > 0:
            pct = ((curr_cat[cat] - prev_cat[cat]) / prev_cat[cat]) * 100
            if pct > 20:
                insights.append(
                    f"⚠️  {cat} spending rose {pct:.0f}% this month "
                    f"(₹{curr_cat[cat]:,.0f} vs ₹{prev_cat[cat]:,.0f})."
                )

    # Anomalies
    anomaly_count = df["is_anomaly"].sum() if "is_anomaly" in df.columns else 0
    if anomaly_count > 0:
        insights.append(f"🚨 {int(anomaly_count)} unusual transaction(s) detected this month.")

    # Top category overall
    top_cat = df.groupby("category")["amount"].sum().idxmax()
    top_amt = df.groupby("category")["amount"].sum().max()
    insights.append(f"🏆 All-time highest spending category: {top_cat} (₹{top_amt:,.0f}).")

    return insights
