"""
streamlit_app.py - Smart Expense Tracker UI with full error handling
"""

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from datetime import date

st.set_page_config(
    page_title="Smart Expense Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
)

API_BASE = st.sidebar.text_input(
    "Backend API URL",
    value="http://127.0.0.1:5000",
)

CATEGORY_COLORS = {
    "Food":          "#FF6B6B",
    "Transport":     "#4ECDC4",
    "Shopping":      "#45B7D1",
    "Entertainment": "#FFA07A",
    "Health":        "#98D8C8",
    "Utilities":     "#DDA0DD",
    "Travel":        "#F0E68C",
    "Education":     "#87CEEB",
    "Uncategorized": "#D3D3D3",
}

# ── Error messages ──────────────────────────────────────────────────────────

def show_backend_error(action="connect to backend"):
    st.error(f"""
**Cannot {action}**

**Reason:** Flask backend is not running.

**Fix:** Open a terminal in VS Code and run:
```
python app.py
```
Make sure you see:  `Running on http://127.0.0.1:5000`
""")

def show_api_error(endpoint, status_code, message):
    st.error(f"""
**API Request Failed**

- **Endpoint:** `{endpoint}`
- **Status Code:** `{status_code}`
- **Error:** {message}

**Fix:** Check your terminal for Flask error logs.
""")

def show_model_error():
    st.warning(f"""
**Model Not Found**

The model file `model.pkl` is missing.

**Fix:** Run this in your terminal:
```
python train_model.py
```
Wait for it to finish, then try again.
""")

def show_timeout_error(endpoint):
    st.error(f"""
**Request Timed Out**

- **Endpoint:** `{endpoint}`

**Possible reasons:**
- Flask is overloaded or stuck
- Something is blocking the connection

**Fix:** Restart Flask — stop it with `Ctrl+C` then run `python app.py` again.
""")

def show_unknown_error(endpoint, error):
    st.error(f"""
**Unexpected Error**

- **Endpoint:** `{endpoint}`
- **Details:** `{str(error)}`

**Fix:** Check your terminal for more details.
""")

# ── API helpers ─────────────────────────────────────────────────────────────

def api_get(path: str):
    endpoint = f"{API_BASE}{path}"
    try:
        r = requests.get(endpoint, timeout=10)
        if r.status_code == 200:
            return r.json().get("data")
        else:
            try:
                msg = r.json().get("message", "Unknown error")
            except Exception:
                msg = r.text or "Unknown error"
            show_api_error(endpoint, r.status_code, msg)
            return None
    except requests.exceptions.ConnectionError:
        show_backend_error()
        return None
    except requests.exceptions.Timeout:
        show_timeout_error(endpoint)
        return None
    except Exception as e:
        show_unknown_error(endpoint, e)
        return None


def api_post(path: str, payload: dict):
    endpoint = f"{API_BASE}{path}"
    try:
        r = requests.post(endpoint, json=payload, timeout=10)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        show_backend_error(f"POST to {path}")
        return None, 0
    except requests.exceptions.Timeout:
        show_timeout_error(endpoint)
        return None, 0
    except Exception as e:
        show_unknown_error(endpoint, e)
        return None, 0


def api_delete(path: str):
    endpoint = f"{API_BASE}{path}"
    try:
        r = requests.delete(endpoint, timeout=10)
        return r.json(), r.status_code
    except requests.exceptions.ConnectionError:
        show_backend_error(f"DELETE {path}")
        return None, 0
    except requests.exceptions.Timeout:
        show_timeout_error(endpoint)
        return None, 0
    except Exception as e:
        show_unknown_error(endpoint, e)
        return None, 0


# ── Sidebar ─────────────────────────────────────────────────────────────────

st.sidebar.title("Smart Expense Tracker")
st.sidebar.markdown("Expense management")
st.sidebar.divider()

page = st.sidebar.radio("Navigate", [
    "Add Expense",
    "Expenses",
    "Analytics",
    "Forecast",
    "Insights",
], label_visibility="collapsed")

st.sidebar.divider()

# Backend status
try:
    r = requests.get(f"{API_BASE}/api/health", timeout=2)
    if r.status_code == 200:
        st.sidebar.success("Backend connected")
    else:
        st.sidebar.warning("Backend error — check terminal")
except requests.exceptions.ConnectionError:
    st.sidebar.error("Backend offline — run `python app.py`")
except requests.exceptions.Timeout:
    st.sidebar.warning("Backend not responding")
except Exception as e:
    st.sidebar.error(f"Error: {str(e)[:50]}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — Add Expense
# ══════════════════════════════════════════════════════════════════════════════

if page == "Add Expense":
    st.title("Add New Expense")
    st.markdown("Describe your expense in plain English. The tracker will suggest a category.")
    st.divider()

    col1, col2 = st.columns([2, 1])

    predicted_category = None
    predicted_confidence = 0
    prediction_available = False

    with col1:
        description = st.text_input(
            "Description",
            placeholder="e.g. paid 20 for auto",
        )

        if description and len(description) > 3:
            try:
                r = requests.post(
                    f"{API_BASE}/api/predict",
                    json={"description": description},
                    timeout=10
                )
                if r.status_code == 200:
                    pred = r.json().get("data", {})
                    predicted_category = pred.get("category", "")
                    predicted_confidence = pred.get("confidence", 0)
                    prediction_available = True
                    if predicted_category and predicted_category != "Uncategorized":
                        st.info(
                            f"Predicted category: {predicted_category} "
                            f"({predicted_confidence:.1f}% confidence)"
                        )
                elif r.status_code == 503:
                    show_model_error()
                else:
                    st.warning(f"Could not predict category. Status: {r.status_code}")
            except requests.exceptions.ConnectionError:
                st.warning("Cannot reach backend to predict category. Is Flask running?")
            except requests.exceptions.Timeout:
                st.warning("Prediction timed out. Flask may be slow.")
            except Exception as e:
                st.warning(f"Prediction error: {str(e)}")

        categories = [""] + sorted(CATEGORY_COLORS.keys())
        default_index = 0
        if prediction_available and predicted_category in categories and predicted_category != "Uncategorized":
            default_index = categories.index(predicted_category)

        selected_category = st.selectbox(
            "Category (optional)",
            categories,
            index=default_index,
        )

    with col2:
        amount = st.number_input("Amount (₹)", min_value=0.01, step=10.0, format="%.2f")

    expense_date = st.date_input("Date", value=date.today())

    st.markdown("")
    submit = st.button("Add Expense", type="primary", use_container_width=True)

    if submit:
        if not description.strip():
            st.warning("Please enter a description.")
        elif amount <= 0:
            st.warning("Please enter a valid amount greater than 0.")
        else:
            payload = {
                "description": description,
                "amount":      amount,
                "date":        str(expense_date),
            }
            if selected_category:
                payload["category"] = selected_category

            data, status = api_post("/api/expenses", payload)

            if status == 201 and data:
                exp = data.get("data", {})
                st.success(
                    f"Expense added. Category: {exp.get('category')} "
                    f"({exp.get('confidence', 0):.1f}% confidence)"
                )
                if exp.get("is_anomaly"):
                    st.warning("This amount looks unusual for this category.")
            elif status == 400 and data:
                st.error(f"Validation error: {data.get('message', 'Invalid input')}")
            elif status == 503:
                show_model_error()
            elif status == 0:
                pass
            else:
                msg = data.get("message", "Unknown error") if data else "No response from server"
                st.error(f"Failed to add expense: {msg}")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — All Expenses
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Expenses":
    st.title("Expenses")
    st.divider()

    expenses = api_get("/api/expenses")

    if expenses is None:
        st.stop()

    if not expenses:
        st.info("No expenses yet. Go to Add Expense to add your first one.")
        st.stop()

    df = pd.DataFrame(expenses)

    col1, col2, col3 = st.columns(3)
    with col1:
        cats = ["All"] + sorted(df["category"].unique().tolist())
        cat_filter = st.selectbox("Category", cats)
    with col2:
        search = st.text_input("Search description", placeholder="pizza, petrol…")
    with col3:
        sort_by = st.selectbox("Sort by", ["Date ↓", "Date ↑", "Amount ↓", "Amount ↑"])

    filtered = df.copy()
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if search:
        filtered = filtered[filtered["description"].str.contains(search, case=False, na=False)]

    sort_map = {
        "Date ↓":   ("date",   False),
        "Date ↑":   ("date",   True),
        "Amount ↓": ("amount", False),
        "Amount ↑": ("amount", True),
    }
    col, asc = sort_map[sort_by]
    filtered = filtered.sort_values(col, ascending=asc)

    total = filtered["amount"].sum()
    anom  = int(filtered["is_anomaly"].sum()) if "is_anomaly" in filtered.columns else 0
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Shown",   f"₹{total:,.2f}")
    m2.metric("Transactions",  len(filtered))
    m3.metric("Anomalies",  anom)

    st.divider()

    if filtered.empty:
        st.info("No expenses match your filter.")
    else:
        for _, row in filtered.iterrows():
            anomaly_badge = "" if row.get("is_anomaly") else ""
            cat_color     = CATEGORY_COLORS.get(row["category"], "#888")

            c1, c2, c3, c4, c5 = st.columns([3, 1.2, 1.2, 0.8, 0.5])
            c1.markdown(f"**{row['description']}**{anomaly_badge}")
            c2.markdown(
                f"<span style='background:{cat_color};padding:2px 8px;"
                f"border-radius:10px;color:#fff;font-size:0.8em'>{row['category']}</span>",
                unsafe_allow_html=True,
            )
            c3.markdown(f"₹ **{row['amount']:,.2f}**")
            c4.markdown(str(row["date"]))
            with c5:
                if st.button("Delete", key=f"del_{row['id']}"):
                    resp, status = api_delete(f"/api/expenses/{row['id']}")
                    if status == 200:
                        st.success("Deleted.")
                        st.rerun()
                    elif status == 404:
                        st.error("Expense not found. It may already be deleted.")
                    elif status == 0:
                        pass  # already shown
                    else:
                        st.error(f"Could not delete. Status: {status}")
            st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — Analytics
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Analytics":
    st.title("Analytics")
    st.divider()

    data = api_get("/api/analytics")
    if data is None:
        st.stop()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Spent",  f"₹{data['total_spent']:,.2f}")
    m2.metric("Transactions", data["total_expenses"])
    m3.metric("Anomalies",    data["anomaly_count"])
    cat_data = data.get("category_totals", [])
    top_cat  = cat_data[0]["category"] if cat_data else "—"
    m4.metric("Top Category", top_cat)

    st.divider()

    if not cat_data:
        st.info("No expense data yet. Add some expenses first.")
        st.stop()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Spending by Category")
        cats   = [c["category"] for c in cat_data]
        totals = [c["total"]    for c in cat_data]
        colors = [CATEGORY_COLORS.get(c, "#888") for c in cats]

        fig, ax = plt.subplots(figsize=(5, 4))
        wedges, texts, autotexts = ax.pie(
            totals, autopct="%1.1f%%", colors=colors,
            startangle=140, pctdistance=0.82,
            wedgeprops=dict(width=0.6),
        )
        for at in autotexts:
            at.set_fontsize(8)
        ax.legend(wedges, cats, loc="lower center",
                  bbox_to_anchor=(0.5, -0.15), ncol=3, fontsize=7, frameon=False)
        ax.set_title("Category Breakdown", fontsize=12, pad=10)
        fig.patch.set_facecolor("none")
        ax.set_facecolor("none")
        st.pyplot(fig, use_container_width=True)

    with col2:
        st.subheader("Monthly Spending Trend")
        monthly = data.get("monthly_totals", [])
        if monthly:
            months = [m["month"] for m in monthly]
            tots   = [m["total"] for m in monthly]

            fig, ax = plt.subplots(figsize=(5, 4))
            bars = ax.bar(months, tots, color="#4ECDC4", edgecolor="white", width=0.5)
            for bar in bars:
                h = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2,
                        h + max(tots) * 0.01,
                        f"₹{h:,.0f}", ha="center", va="bottom", fontsize=7)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
            ax.tick_params(axis="x", rotation=45, labelsize=7)
            ax.spines[["top", "right"]].set_visible(False)
            fig.tight_layout()
            fig.patch.set_facecolor("none")
            ax.set_facecolor("none")
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Add expenses across different months to see the trend chart.")

    st.divider()
    st.subheader("Category Summary Table")
    df_cat = pd.DataFrame(cat_data)
    df_cat.columns = ["Category", "Total (₹)", "Count"]
    df_cat["Total (₹)"] = df_cat["Total (₹)"].map(lambda x: f"₹{x:,.2f}")
    st.dataframe(df_cat, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — Forecast
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Forecast":
    st.title("Expense Forecast")
    st.markdown("Linear regression predicts next month's spending based on your history.")
    st.divider()

    data = api_get("/api/forecast")
    if data is None:
        st.stop()

    if data.get("trend") == "insufficient_data":
        st.warning("""
Not enough data to forecast.

Add expenses across at least 2 different months to enable forecasting.

For example: add some expenses with April dates and some with May dates.
""")
        st.stop()

    pred  = data["predicted_amount"]
    trend = data["trend"]
    n_pts = data["data_points"]

    TREND_LABELS = {
        "increasing": "Spending is rising month over month.",
        "decreasing": "Spending is falling month over month.",
        "stable":     "Spending is consistent month over month.",
    }
    label = TREND_LABELS.get(trend, "Unknown trend.")

    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Next Month", f"₹{pred:,.2f}")
    c2.metric("Trend", trend.title())
    c3.metric("Months of Data", n_pts)

    st.info(f"Trend: {label}")

    monthly = api_get("/api/analytics")
    if monthly:
        hist = monthly.get("monthly_totals", [])
        if hist:
            months  = [m["month"] for m in hist] + ["Next Month"]
            amounts = [m["total"] for m in hist] + [pred]

            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(months[:-1], amounts[:-1], marker="o", color="#4ECDC4",
                    linewidth=2, label="Actual")
            ax.plot(months[-2:], amounts[-2:], marker="o", color="#FF6B6B",
                    linewidth=2, linestyle="--", label="Forecast")
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{x:,.0f}"))
            ax.tick_params(axis="x", rotation=45, labelsize=8)
            ax.spines[["top", "right"]].set_visible(False)
            ax.legend(fontsize=9)
            ax.set_title("Expense History + AI Forecast", fontsize=12)
            fig.tight_layout()
            fig.patch.set_facecolor("none")
            ax.set_facecolor("none")
            st.pyplot(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — AI Insights
# ══════════════════════════════════════════════════════════════════════════════

elif page == "Insights":
    st.title("Insights")
    st.markdown("Analysis of your spending patterns.")
    st.divider()

    insights = api_get("/api/insights")
    if insights is None:
        st.stop()

    if not insights:
        st.info("No insights yet. Add more expenses first.")
        st.stop()

    for insight in insights:
        st.markdown(
            f"""
            <div style="
                background: rgba(255,255,255,0.05);
                border-left: 4px solid #4ECDC4;
                padding: 12px 16px;
                border-radius: 8px;
                margin-bottom: 12px;
                font-size: 1rem;
            ">
                {insight}
            </div>
            """,
            unsafe_allow_html=True,
        )