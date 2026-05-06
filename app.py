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
    else:
        try:
            prediction = ml.predict_category(description)
            category   = prediction["category"]
            confidence = prediction["confidence"]
        except FileNotFoundError:
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


# ─── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 50)
    print("  Smart Expense Tracker API  ")
    print("  Running at http://127.0.0.1:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
