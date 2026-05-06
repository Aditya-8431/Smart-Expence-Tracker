# 💰 Smart Expense Tracker with AI

> An intelligent expense management system built with **Python, Flask, SQLite, Scikit-learn, and Streamlit**.  
> AI auto-categorises expenses, detects anomalies, forecasts next-month spending, and generates smart insights.

---

## 🧠 Tech Stack

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| Language       | Python 3.10+                            |
| Backend API    | Flask + Flask-CORS                      |
| Database       | SQLite                                  |
| ML / NLP       | Scikit-learn, TF-IDF, Random Forest     |
| Forecasting    | Linear Regression                       |
| Anomaly        | Z-score (per-category stats)            |
| Data           | Pandas, NumPy                           |
| Visualisation  | Matplotlib                              |
| Frontend       | Streamlit                               |
| Model Saving   | Joblib                                  |

---

## 📁 Project Structure

```
Smart-Expense-Tracker/
│
├── backend/
│   ├── __init__.py       # Package marker
│   ├── app.py            # Flask REST API (all routes)
│   ├── database.py       # SQLite CRUD operations
│   └── ml_model.py       # ML inference: predict, anomaly, forecast, insights
│
├── training/
│   ├── train_model.py    # Training pipeline — run this first
│   └── model.pkl         # Saved model (generated after training)
│
├── frontend/
│   └── streamlit_app.py  # Full Streamlit UI
│
├── requirements.txt
└── README.md
```

---

## 🚀 Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train the ML model (run once)
```bash
python training/train_model.py
```
This creates `training/model.pkl`.

### 3. Start the Flask backend
```bash
cd backend
python app.py
```
API runs at `http://127.0.0.1:5000`

### 4. Launch the Streamlit frontend (new terminal)
```bash
streamlit run frontend/streamlit_app.py
```
UI opens at `http://localhost:8501`

---

## 🔌 API Reference

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| GET    | `/api/health`             | Health check                       |
| POST   | `/api/expenses`           | Add new expense (AI auto-tags)     |
| GET    | `/api/expenses`           | Get all expenses                   |
| DELETE | `/api/expenses/<id>`      | Delete an expense                  |
| POST   | `/api/predict`            | Predict category from description  |
| GET    | `/api/analytics`          | Category totals + monthly totals   |
| GET    | `/api/forecast`           | Next-month prediction              |
| GET    | `/api/insights`           | Smart AI insights                  |

### Example — Add expense
```bash
curl -X POST http://127.0.0.1:5000/api/expenses \
     -H "Content-Type: application/json" \
     -d '{"description": "paid 450 for pizza", "amount": 450, "date": "2025-05-01"}'
```

---

## 🤖 AI Features

| Feature              | Algorithm            | What It Does                              |
|----------------------|----------------------|-------------------------------------------|
| Category Prediction  | TF-IDF + Random Forest | Auto-tags expenses (Food, Transport…)   |
| Anomaly Detection    | Z-score (σ > 2)      | Flags unusually large expenses            |
| Forecasting          | Linear Regression    | Predicts next month's total spending      |
| Smart Insights       | Statistics + Rules   | "You spent 30% more on Food this month"   |

---

## 📊 Categories Supported

Food · Transport · Shopping · Entertainment · Health · Utilities · Travel · Education

---

## 🏗 Architecture

```
User
 ↓
Streamlit Frontend (port 8501)
 ↓  REST API calls
Flask Backend (port 5000)
 ↓              ↓
SQLite DB    ML Model (Scikit-learn)
```

---

## 📌 After 30 Days You Will Know

- ✅ Build and deploy REST APIs
- ✅ Train and serve ML classification models
- ✅ Use NLP (TF-IDF) for text classification
- ✅ Anomaly detection with statistical methods
- ✅ Time-series forecasting with Linear Regression
- ✅ Build production-ready Python backends
- ✅ Create interactive ML dashboards with Streamlit

---

*Built as part of the 30-Day AI Engineer Roadmap.*
