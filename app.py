"""
app.py
------
Flask REST API for Smart Expense Tracker.

Routes
------
POST   /api/expenses          → Add a new expense
GET    /api/expenses          → Get all expenses
DELETE /api/expenses/<id>     → Delete an expense
POST   /api/predict           → Predict category from description
GET    /api/analytics         → Category totals + monthly totals
GET    /api/forecast          → Next-month prediction
GET    /api/insights          → Smart AI insights
GET    /api/health            → Health check
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import date as dt_date

import database as db
import ml_model  as ml

app = Flask(__name__)
CORS(app)   # Allow Streamlit frontend to call this API


# ─── Helper ────────────────────────────────────────────────────────────────

def _ok(data=None, message="success", status=200):
    return jsonify({"status": "ok", "message": message, "data": data}), status


def _err(message, status=400):
    return jsonify({"status": "error", "message": message, "data": None}), status


# ─── Health ─────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return _ok({"service": "Smart Expense Tracker API", "version": "1.0.0"})


# ─── Expenses ───────────────────────────────────────────────────────────────

@app.route("/api/expenses", methods=["POST"])
def add_expense():
    """
    Body (JSON):
      description : str
      amount      : float
      date        : str  (YYYY-MM-DD, optional, defaults to today)
      category    : str  (optional; use manual category instead of model prediction)
    """
    body = request.get_json(silent=True) or {}

    description = str(body.get("description", "")).strip()
    amount_raw  = body.get("amount")
    expense_date = str(body.get("date", str(dt_date.today())))
    category_override = str(body.get("category", "") or "").strip()

    if not description:
        return _err("description is required.")
    if amount_raw is None:
        return _err("amount is required.")

    try:
        amount = float(amount_raw)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return _err("amount must be a positive number.")

    # 1. Use manual category when provided, otherwise predict category
    if category_override:
        prediction = {"category": category_override, "confidence": 100.0}
        category   = category_override
        confidence = 100.0
        try:
            ml.save_manual_category(description, category_override)
        except Exception as exc:
            print(f"[WARNING] Failed to save manual category mapping: {exc}")
    else:
        try:
            prediction = ml.predict_category(description)
            category   = prediction["category"]
            confidence = prediction["confidence"]
        except FileNotFoundError:
            category   = "Uncategorized"
            confidence = 0.0
        except Exception as exc:
            print(f"[ERROR] Category prediction failed: {exc}")
            category   = "Uncategorized"
            confidence = 0.0

    # 2. Detect anomaly
    existing    = db.get_all_expenses()
    is_anomaly  = ml.detect_anomaly(amount, category, existing)

    # 3. Save to DB
    expense = db.add_expense(
        description=description,
        amount=amount,
        category=category,
        date=expense_date,
        is_anomaly=int(is_anomaly),
    )

    expense["predicted_category"] = category
    expense["confidence"]         = confidence
    expense["is_anomaly"]         = is_anomaly

    return _ok(expense, message="Expense added successfully.", status=201)

@app.route("/")
def home():
    return "Smart Expense Tracker API Running"

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    expenses = db.get_all_expenses()
    return _ok(expenses)


@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    deleted = db.delete_expense(expense_id)
    if deleted:
        return _ok(message=f"Expense {expense_id} deleted.")
    return _err(f"Expense {expense_id} not found.", status=404)


# ─── Predict ────────────────────────────────────────────────────────────────

@app.route("/api/predict", methods=["POST"])
def predict():
    """
    Body (JSON):
      description : str
    """
    body        = request.get_json(silent=True) or {}
    description = str(body.get("description", "")).strip()

    if not description:
        return _err("description is required.")

    try:
        result = ml.predict_category(description)
        return _ok(result)
    except FileNotFoundError as exc:
        return _err(str(exc), status=503)
    except Exception as exc:
        print(f"[ERROR] Prediction endpoint failed: {exc}")
        return _err(f"Prediction failed: {exc}", status=500)


# ─── Analytics ──────────────────────────────────────────────────────────────

@app.route("/api/analytics", methods=["GET"])
def analytics():
    category_totals = db.get_category_totals()
    monthly_totals  = db.get_monthly_totals()
    all_expenses    = db.get_all_expenses()

    total_spent   = sum(e["amount"] for e in all_expenses)
    anomaly_count = sum(1 for e in all_expenses if e.get("is_anomaly"))

    return _ok({
        "total_spent":      round(total_spent, 2),
        "total_expenses":   len(all_expenses),
        "anomaly_count":    anomaly_count,
        "category_totals":  category_totals,
        "monthly_totals":   monthly_totals, 
    })


# ─── Forecast ───────────────────────────────────────────────────────────────

@app.route("/api/forecast", methods=["GET"])
def forecast():
    monthly_totals = db.get_monthly_totals()
    result         = ml.forecast_next_month(monthly_totals)
    return _ok(result)


# ─── Insights ───────────────────────────────────────────────────────────────

@app.route("/api/insights", methods=["GET"])
def insights():
    all_expenses = db.get_all_expenses()
    result       = ml.generate_insights(all_expenses)
    return _ok(result)


# ─── Budgets ────────────────────────────────────────────────────────────────

@app.route("/api/budgets", methods=["POST"])
def add_budget():
    """Add a new budget for a category.
    Body (JSON):
      category : str (e.g., 'Food', 'Transport')
      amount   : float (budget limit)
      period   : str ('weekly' or 'monthly')
    """
    body = request.get_json(silent=True) or {}
    
    category = str(body.get("category", "")).strip()
    amount = body.get("amount")
    period = str(body.get("period", "")).strip()
    
    if not category:
        return _err("category is required.")
    if amount is None:
        return _err("amount is required.")
    if period not in ["weekly", "monthly"]:
        return _err("period must be 'weekly' or 'monthly'.")
    
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return _err("amount must be a positive number.")
    
    budget = db.add_budget(category, amount, period)
    return _ok(budget, message="Budget added successfully.", status=201)


@app.route("/api/budgets", methods=["GET"])
def get_budgets():
    """Get all budgets."""
    budgets = db.get_all_budgets()
    return _ok(budgets)


@app.route("/api/budgets/<category>/<period>", methods=["DELETE"])
def delete_budget(category, period):
    """Delete a budget by category and period."""
    deleted = db.delete_budget(category, period)
    if deleted:
        return _ok(message=f"Budget for {category} ({period}) deleted.")
    return _err(f"Budget for {category} ({period}) not found.", status=404)


@app.route("/api/budget-report", methods=["GET"])
def budget_report():
    """Get spending vs budget report for all categories."""
    from datetime import datetime, timedelta
    
    all_budgets = db.get_all_budgets()
    all_expenses = db.get_all_expenses()
    today = datetime.strptime(str(dt_date.today()), "%Y-%m-%d")
    
    report = []
    
    for budget in all_budgets:
        category = budget["category"]
        budget_amount = budget["amount"]
        period = budget["period"]
        
        # Calculate spending for this period
        if period == "weekly":
            # Last 7 days
            week_ago = today - timedelta(days=7)
            expenses = [e for e in all_expenses 
                       if e["category"] == category 
                       and datetime.strptime(e["date"], "%Y-%m-%d") >= week_ago]
        else:  # monthly
            # Current month
            month_str = today.strftime("%Y-%m")
            expenses = [e for e in all_expenses 
                       if e["category"] == category 
                       and e["date"].startswith(month_str)]
        
        spent = sum(e["amount"] for e in expenses)
        remaining = budget_amount - spent
        percentage = round((spent / budget_amount * 100) if budget_amount > 0 else 0, 1)
        
        # Status: green if under, yellow if 80%+, red if over
        if remaining >= 0 and percentage < 80:
            status = "good"
        elif remaining >= 0:
            status = "warning"
        else:
            status = "over"
        
        report.append({
            "category": category,
            "period": period,
            "budget": budget_amount,
            "spent": round(spent, 2),
            "remaining": round(remaining, 2),
            "percentage": percentage,
            "status": status
        })
    
    return _ok(report)


# ─── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    try:
        ml._load_model()
        print("[INFO] ML model loaded successfully.")
    except FileNotFoundError:
        print("[WARNING] ML model not found. Run python train_model.py to generate it.")
    except Exception as exc:
        print(f"[ERROR] Failed to preload ML model: {exc}")

    print("=" * 50)
    print("  Smart Expense Tracker API  ")
    print("  Running at http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
