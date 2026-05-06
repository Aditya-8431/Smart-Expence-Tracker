# 💰 Smart Expense Tracker with AI

An intelligent expense management system that leverages machine learning to automatically categorize expenses, detect anomalies, forecast spending patterns, and provide actionable financial insights. Built with Python, Flask, SQLite, Scikit-learn, and Streamlit.

**Live Demo** · [Report Bug](../../issues) · [Request Feature](../../issues)

---

## 🖼️ Screenshots

### Expenses dashboard
![Expenses dashboard](images/expenses-dashboard.png)

### Add expense screen
![Add expense screen](images/add-expense-screen.png)

---

## ✨ Key Features

- **🤖 AI-Powered Categorization** — Automatically categorizes expenses using TF-IDF and Random Forest algorithms
- **🚨 Anomaly Detection** — Identifies unusual spending patterns using statistical Z-score analysis
- **📈 Predictive Forecasting** — Forecasts next month's spending using Linear Regression
- **💡 Smart Insights** — Generates actionable insights like "30% higher spending on Food this month"
- **📊 Real-Time Analytics** — Track spending by category, time period, and trends
- **🎯 Multi-Category Support** — 8 predefined categories with extensible architecture
- **⚡ REST API** — Fully-documented REST endpoints for programmatic access
- **🎨 Interactive Dashboard** — Professional Streamlit UI for visualization and management

---

## 🧠 Technology Stack

| Component      | Technology                                  |
|----------------|---------------------------------------------|
| **Language**   | Python 3.10+                                |
| **Backend**    | Flask + Flask-CORS                          |
| **Database**   | SQLite                                      |
| **ML/NLP**     | Scikit-learn, TF-IDF, Random Forest         |
| **Forecasting**| Linear Regression                           |
| **Anomaly**    | Z-score statistical analysis                |
| **Data**       | Pandas, NumPy                               |
| **Visualization** | Matplotlib                              |
| **Frontend**   | Streamlit                                   |
| **Serialization** | Joblib                                  |

---

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.10 or higher**
- **pip** (Python package manager)
- **Git** (optional, for cloning the repository)
- **curl** (optional, for testing API endpoints)

---

## 📁 Project Structure

```
Smart-Expense-Tracker/
│
├── backend/
│   ├── __init__.py              # Package initialization
│   ├── app.py                   # Flask REST API server (all routes)
│   ├── database.py              # SQLite database operations (CRUD)
│   └── ml_model.py              # ML inference engine (predict, anomaly, forecast, insights)
│
├── training/
│   ├── train_model.py           # Model training pipeline (run once initially)
│   └── model.pkl                # Serialized trained model (auto-generated)
│
├── frontend/
│   └── streamlit_app.py         # Interactive Streamlit dashboard
│
├── requirements.txt             # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Train the ML Model

Run this **once** to generate the trained model:

```bash
python training/train_model.py
```

This creates `training/model.pkl` which is used for inference.

### 3️⃣ Start the Flask Backend

```bash
cd backend
python app.py
```

The API will be available at **http://127.0.0.1:5000**

### 4️⃣ Launch the Streamlit Frontend

Open a **new terminal** and run:

```bash
streamlit run frontend/streamlit_app.py
```

The interactive dashboard will open at **http://localhost:8501**

---

## 🔌 API Reference

### Core Endpoints

| Method | Endpoint              | Description                          | Auth |
|--------|----------------------|--------------------------------------|------|
| `GET`  | `/api/health`        | System health check                  | No   |
| `POST` | `/api/expenses`      | Create new expense (auto-categorized) | No   |
| `GET`  | `/api/expenses`      | Retrieve all expenses                | No   |
| `DELETE` | `/api/expenses/<id>` | Delete specific expense              | No   |

### Analytics & Prediction Endpoints

| Method | Endpoint           | Description                        | Auth |
|--------|--------------------|------------------------------------|------|
| `POST` | `/api/predict`     | Predict category for description   | No   |
| `GET`  | `/api/analytics`   | Get spending analytics by category | No   |
| `GET`  | `/api/forecast`    | Forecast next month's spending     | No   |
| `GET`  | `/api/insights`    | Generate smart spending insights   | No   |

### Example Requests

#### Add New Expense
```bash
curl -X POST http://127.0.0.1:5000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Lunch at Italian restaurant",
    "amount": 25.50,
    "date": "2025-05-01"
  }'
```

#### Predict Category
```bash
curl -X POST http://127.0.0.1:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"description": "Uber ride downtown"}'
```

#### Get Analytics
```bash
curl http://127.0.0.1:5000/api/analytics
```

#### Get Forecast
```bash
curl http://127.0.0.1:5000/api/forecast
```

---

## 🤖 AI Features

### Category Prediction
- **Algorithm:** TF-IDF + Random Forest Classification
- **Purpose:** Automatically tags expenses into predefined categories
- **Accuracy:** Improves with more labeled expense data

### Anomaly Detection
- **Algorithm:** Z-score Statistical Analysis (σ > 2)
- **Purpose:** Identifies unusually high expenses within each category
- **Use Case:** Detect fraudulent or unexpected transactions

### Spending Forecast
- **Algorithm:** Linear Regression
- **Purpose:** Predicts total spending for the next month
- **Use Case:** Budget planning and financial forecasting

### Smart Insights
- **Algorithm:** Statistical Analysis + Business Rules
- **Examples:**
  - "30% higher spending on Food compared to last month"
  - "Transport costs increased by $120"
  - "Entertainment spending is within normal range"

---

## 📊 Supported Expense Categories

- **Food** — Restaurants, groceries, delivery
- **Transport** — Gas, public transit, ride-sharing, parking
- **Shopping** — Retail purchases, online shopping
- **Entertainment** — Movies, events, hobbies
- **Health** — Medical, fitness, wellness
- **Utilities** — Electricity, water, internet
- **Travel** — Hotels, flights, vacation
- **Education** — Courses, books, training

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────┐
│         User / Web Browser              │
└────────────┬────────────────────────────┘
             │
             ↓
┌─────────────────────────────────────────┐
│   Streamlit Frontend (Port 8501)        │
│   • Dashboard & Visualization           │
│   • Form Input & Management             │
└────────────┬────────────────────────────┘
             │
             ↓ (REST API Calls)
┌─────────────────────────────────────────┐
│   Flask Backend (Port 5000)             │
│   • API Routes & Business Logic         │
└─────┬──────────────────────┬────────────┘
      │                      │
      ↓                      ↓
┌──────────────┐       ┌───────────────────┐
│  SQLite DB   │       │  ML Model (Joblib)│
│  • Expenses  │       │  • Classifier     │
│  • Metadata  │       │  • Forecaster     │
└──────────────┘       └───────────────────┘
```

---

## 📚 Learning Outcomes

By working through this project, you will master:

- ✅ Building RESTful APIs with Flask
- ✅ Training and deploying ML classification models
- ✅ Natural Language Processing (NLP) with TF-IDF
- ✅ Anomaly detection using statistical methods
- ✅ Time-series forecasting with Linear Regression
- ✅ SQLite database design and CRUD operations
- ✅ Building interactive dashboards with Streamlit
- ✅ Model persistence and serialization (Joblib)
- ✅ Production-ready Python backends

---

## 🔧 Configuration

### Model Training Parameters

Edit `training/train_model.py` to adjust:
- Training data ratio
- Random Forest hyperparameters
- Category mappings
- Anomaly threshold (Z-score)

### Flask Settings

Configure in `backend/app.py`:
- Port number (default: 5000)
- CORS origins
- Database location

### Streamlit Settings

Configure in `frontend/streamlit_app.py`:
- Page layout and theme
- Chart configurations
- API endpoint URL

---

## 🐛 Troubleshooting

### Issue: Model file not found
**Solution:** Run `python training/train_model.py` to generate the model first.

### Issue: Port 5000 already in use
**Solution:** Change the port in `backend/app.py` or kill the process using the port.

### Issue: Module import errors
**Solution:** Ensure all dependencies are installed: `pip install -r requirements.txt`

### Issue: API calls failing from Streamlit
**Solution:** Verify Flask backend is running and check CORS settings in `backend/app.py`.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📧 Support & Contact

For questions, suggestions, or issues:
- **GitHub Issues:** [Open an issue](../../issues)
- **Email:** your-email@example.com

---

## 🎓 Learning Resources

- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
- [Linear Regression Guide](https://en.wikipedia.org/wiki/Linear_regression)

---

## ✍️ Changelog

### Version 1.0 (Current)
- Initial release with core features
- 8 expense categories
- ML-based categorization and forecasting
- Anomaly detection system
- Interactive Streamlit dashboard

---

**Built with ❤️ as part of the 30-Day AI Engineer Roadmap**
