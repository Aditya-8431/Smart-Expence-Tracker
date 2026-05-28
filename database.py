"""
database.py
-----------
Handles all SQLite database operations for Smart Expense Tracker.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def get_connection():
    """Returns a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Creates the expenses and budgets tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            is_anomaly  INTEGER DEFAULT 0,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    
    # Create budgets table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            period      TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()
    print("[DB] Database initialized.")


def add_expense(description: str, amount: float, category: str, date: str, is_anomaly: int = 0) -> dict:
    """Insert a new expense record and return it."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (description, amount, category, date, is_anomaly)
        VALUES (?, ?, ?, ?, ?)
    """, (description, amount, category, date, is_anomaly))
    conn.commit()
    expense_id = cursor.lastrowid
    conn.close()
    return get_expense_by_id(expense_id)


def get_expense_by_id(expense_id: int) -> dict:
    """Fetch a single expense by its ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_expenses() -> list:
    """Return all expenses ordered by date descending."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC, created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_expenses_by_month(year: int, month: int) -> list:
    """Return all expenses for a given year-month."""
    month_str = f"{year}-{str(month).zfill(2)}"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE strftime('%Y-%m', date) = ?", (month_str,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_monthly_totals() -> list:
    """Return total spending per month across all records."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT strftime('%Y-%m', date) AS month,
               SUM(amount)            AS total
        FROM   expenses
        GROUP  BY month
        ORDER  BY month
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_category_totals() -> list:
    """Return total spending per category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT category,
               SUM(amount)   AS total,
               COUNT(*)      AS count
        FROM   expenses
        GROUP  BY category
        ORDER  BY total DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_expense(expense_id: int) -> bool:
    """Delete an expense by ID. Returns True if deleted."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# ─── BUDGET FUNCTIONS ───────────────────────────────────────────────────────

def add_budget(category: str, amount: float, period: str) -> dict:
    """Add a new budget. period should be 'weekly' or 'monthly'."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete old budget if exists (replace it)
    cursor.execute("DELETE FROM budgets WHERE category = ? AND period = ?", (category, period))
    
    # Add new budget
    cursor.execute("""
        INSERT INTO budgets (category, amount, period)
        VALUES (?, ?, ?)
    """, (category, amount, period))
    conn.commit()
    budget_id = cursor.lastrowid
    conn.close()
    return get_budget_by_id(budget_id)


def get_budget_by_id(budget_id: int) -> dict:
    """Get a single budget by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets WHERE id = ?", (budget_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_all_budgets() -> list:
    """Get all budgets."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets ORDER BY category")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_budget(category: str, period: str) -> dict:
    """Get budget for a specific category and period."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM budgets WHERE category = ? AND period = ?", (category, period))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def delete_budget(category: str, period: str) -> bool:
    """Delete a budget by category and period."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE category = ? AND period = ?", (category, period))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0


# Auto-initialize on import
init_db()
