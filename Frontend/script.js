// =====================================================
// script.js - Smart Expense Tracker
// 
// What this file does:
// 1. Connects to Flask backend using fetch()
// 2. Adds, loads, deletes expenses
// 3. Shows charts using Chart.js
// 4. Switches between pages (Add, History, Reports, etc.)
//
// KEY CONCEPT: fetch() is how JavaScript talks to Flask.
// It sends an HTTP request and gets JSON back.
// =====================================================


// =====================================================
// CONFIGURATION
// =====================================================

// Flask backend URL - change this if your Flask runs on a different port
const API_URL = "http://127.0.0.1:5000";

// If AI confidence is below this number, show the manual category picker
const CONFIDENCE_LIMIT = 65;

// Colors for each category - used in the table and charts
const CATEGORY_COLORS = {
    "Food":          "#E76F51",
    "Transport":     "#2A9D8F",
    "Shopping":      "#4895EF",
    "Entertainment": "#F4A261",
    "Health":        "#57CC99",
    "Utilities":     "#9B72CF",
    "Travel":        "#E9C46A",
    "Education":     "#48CAE4",
    "Other":         "#ADB5BD"
};


// =====================================================
// GLOBAL VARIABLES
// =====================================================

// Stores all expenses fetched from Flask (used for filtering)
let allExpenses = [];

// Stores Chart.js chart objects so we can destroy + redraw them
let pieChart = null;
let barChart = null;


// =====================================================
// 1. CHECK BACKEND STATUS
// Runs on page load - shows if Flask is online or offline
// =====================================================
async function checkBackendStatus() {
    const statusEl = document.getElementById("status-indicator");

    try {
        // Try to call the health check endpoint
        const response = await fetch(`${API_URL}/api/health`);

        if (response.ok) {
            // Flask is running - show green
            statusEl.textContent = "● Backend Online";
            statusEl.className   = "status-indicator status-online";
        } else {
            statusEl.textContent = "● Backend Error";
            statusEl.className   = "status-indicator status-offline";
        }

    } catch (error) {
        // fetch() failed - Flask is probably not running
        statusEl.textContent = "● Backend Offline";
        statusEl.className   = "status-indicator status-offline";
    }
}


// =====================================================
// 2. SWITCH BETWEEN PAGES
// Called by each nav button onclick
// 
// pageName   - which page to show ("add", "history", etc.)
// clickedBtn - the button that was clicked (so we can mark it active)
// =====================================================
function showPage(pageName, clickedBtn) {

    // Step 1: Hide ALL pages
    const allPages = document.querySelectorAll(".page");
    allPages.forEach(function(page) {
        page.classList.remove("active");
    });

    // Step 2: Remove "active" from ALL nav buttons
    const allBtns = document.querySelectorAll(".nav-btn");
    allBtns.forEach(function(btn) {
        btn.classList.remove("active");
    });

    // Step 3: Show only the selected page
    document.getElementById("page-" + pageName).classList.add("active");

    // Step 4: Mark the clicked button as active
    clickedBtn.classList.add("active");

    // Step 5: Load data for the page
    if (pageName === "history")     loadExpenses();
    if (pageName === "reports")     loadReports();
    if (pageName === "predictions") loadPrediction();
    if (pageName === "budget")      loadBudgets();
    if (pageName === "tips")        loadTips();
}


// =====================================================
// 3. AI CATEGORY PREVIEW
// Called every time the user types in the description box
// Sends the text to Flask and shows AI prediction
// =====================================================
async function previewCategory() {
    const description = document.getElementById("input-description").value;
    const predEl      = document.getElementById("ai-prediction");
    const manualBox   = document.getElementById("manual-category-box");

    // Don't call API if less than 3 characters typed
    if (description.length < 3) {
        predEl.innerHTML        = "";
        manualBox.style.display = "none";
        return;
    }

    try {
        // Call the Flask predict endpoint
        const response = await fetch(`${API_URL}/api/predict`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ description: description })
        });

        const result   = await response.json();
        const category   = result.data.category;
        const confidence = result.data.confidence;
        const color      = CATEGORY_COLORS[category] || "#888";

        if (confidence >= CONFIDENCE_LIMIT) {
            // AI is confident - show green badge, hide manual picker
            predEl.innerHTML = `
                <div class="badge-confident">
                    AI predicts: <strong style="color: ${color}">${category}</strong>
                    &nbsp;—&nbsp; ${confidence.toFixed(0)}% confident
                </div>`;
            manualBox.style.display = "none";

        } else {
            // AI is NOT confident - show yellow badge, show manual picker
            predEl.innerHTML = `
                <div class="badge-unsure">
                    Not sure (${confidence.toFixed(0)}% confidence) — please select category below
                </div>`;
            manualBox.style.display = "block";
        }

    } catch (error) {
        // Flask is not reachable
        predEl.innerHTML = `<p style="color: #999; font-size: 13px; margin-top: 8px;">
            Cannot reach backend to predict. Is Flask running?
        </p>`;
    }
}


// =====================================================
// 4. ADD EXPENSE
// Called when user clicks the "Add Expense" button
// Reads form values and sends them to Flask
// =====================================================
async function addExpense() {
    // Get the values from the form inputs
    const description = document.getElementById("input-description").value.trim();
    const amount      = document.getElementById("input-amount").value;
    const date        = document.getElementById("input-date").value;
    const messageEl   = document.getElementById("add-message");
    const manualBox   = document.getElementById("manual-category-box");

    // --- Validate: check all fields are filled ---
    if (!description) {
        messageEl.innerHTML = `<div class="msg-error">Please enter a description.</div>`;
        return;
    }
    if (!amount || Number(amount) <= 0) {
        messageEl.innerHTML = `<div class="msg-error">Please enter a valid amount.</div>`;
        return;
    }
    if (!date) {
        messageEl.innerHTML = `<div class="msg-error">Please select a date.</div>`;
        return;
    }

    // Build the data object to send to Flask
    const requestBody = {
        description: description,
        amount:      parseFloat(amount),
        date:        date
    };

    // If manual picker is visible, add the selected category to the request
    if (manualBox.style.display === "block") {
        requestBody.category = document.getElementById("manual-category").value;
    }

    try {
        // Send POST request to Flask
        const response = await fetch(`${API_URL}/api/expenses`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify(requestBody)
        });

        const result = await response.json();

        if (response.status === 201) {
            // SUCCESS - expense was added
            const expense = result.data;
            let successMsg = `Expense added! Category: <strong>${expense.category}</strong>`;

            // Show a warning if anomaly was detected
            if (expense.is_anomaly) {
                successMsg += `<br><span style="color: #E76F51">
                    Warning: This amount is higher than usual for ${expense.category}.
                </span>`;
            }

            messageEl.innerHTML = `<div class="msg-success">${successMsg}</div>`;

            // Clear the form after adding
            document.getElementById("input-description").value = "";
            document.getElementById("input-amount").value      = "";
            document.getElementById("ai-prediction").innerHTML = "";
            manualBox.style.display = "none";

        } else {
            // Flask returned an error
            messageEl.innerHTML = `<div class="msg-error">Error: ${result.message}</div>`;
        }

    } catch (error) {
        // fetch() failed - Flask is not running
        messageEl.innerHTML = `
            <div class="msg-error">
                Cannot connect to Flask. Make sure Flask is running.<br>
                Open a terminal and run: <strong>python app.py</strong>
            </div>`;
    }
}


// =====================================================
// 5. LOAD ALL EXPENSES (History page)
// Fetches all expenses from Flask and shows them in a table
// =====================================================
async function loadExpenses() {
    const tbody = document.getElementById("expense-tbody");
    tbody.innerHTML = `<tr><td colspan="5" class="loading">Loading expenses...</td></tr>`;

    try {
        const response = await fetch(`${API_URL}/api/expenses`);
        const result   = await response.json();

        // Save to global variable (used for filtering)
        allExpenses = result.data;

        // Update the 3 summary cards
        const totalAmount = allExpenses.reduce(function(sum, e) { return sum + e.amount; }, 0);
        const anomalyCount = allExpenses.filter(function(e) { return e.is_anomaly; }).length;

        document.getElementById("total-spent").textContent    = "₹" + totalAmount.toFixed(2);
        document.getElementById("total-count").textContent    = allExpenses.length;
        document.getElementById("total-anomalies").textContent = anomalyCount;

        // Render the table rows
        renderTable(allExpenses);

    } catch (error) {
        tbody.innerHTML = `
            <tr><td colspan="5" class="msg-error" style="padding: 20px">
                Cannot load expenses. Is Flask running?
                Run: <strong>python app.py</strong>
            </td></tr>`;
    }
}


// =====================================================
// 6. RENDER TABLE ROWS
// Takes an array of expenses and builds HTML table rows
// Called by loadExpenses() and filterExpenses()
// =====================================================
function renderTable(expenses) {
    const tbody = document.getElementById("expense-tbody");

    // No expenses - show empty state
    if (expenses.length === 0) {
        tbody.innerHTML = `
            <tr><td colspan="5" class="empty-state">
                No expenses found.
            </td></tr>`;
        return;
    }

    // Build HTML for all rows
    let html = "";

    expenses.forEach(function(expense) {
        const color      = CATEGORY_COLORS[expense.category] || "#888";
        const anomalyBadge = expense.is_anomaly
            ? `<span class="anomaly-flag">⚠ unusual amount</span>`
            : "";

        html += `
            <tr>
                <td>
                    ${expense.description}
                    ${anomalyBadge}
                </td>
                <td>
                    <span class="cat-badge" style="background-color: ${color}">
                        ${expense.category}
                    </span>
                </td>
                <td>₹${expense.amount.toFixed(2)}</td>
                <td>${expense.date}</td>
                <td>
                    <button class="btn-delete" onclick="deleteExpense(${expense.id})">
                        Delete
                    </button>
                </td>
            </tr>`;
    });

    tbody.innerHTML = html;
}


// =====================================================
// 7. FILTER EXPENSES
// Called when user types in search box or changes category
// Filters the global allExpenses array and re-renders table
// =====================================================
function filterExpenses() {
    const searchText = document.getElementById("search-input").value.toLowerCase();
    const category   = document.getElementById("filter-category").value;

    // Filter the array
    const filtered = allExpenses.filter(function(expense) {
        const matchesSearch   = expense.description.toLowerCase().includes(searchText);
        const matchesCategory = (category === "All") || (expense.category === category);
        return matchesSearch && matchesCategory;
    });

    renderTable(filtered);
}


// =====================================================
// 8. DELETE EXPENSE
// Asks for confirmation, then sends DELETE request to Flask
// =====================================================
async function deleteExpense(id) {
    // Ask user to confirm before deleting
    const confirmed = confirm("Are you sure you want to delete this expense?");
    if (!confirmed) return;

    try {
        const response = await fetch(`${API_URL}/api/expenses/${id}`, {
            method: "DELETE"
        });

        if (response.status === 200) {
            // Step 1: Hide ALL pages
            const allPages = document.querySelectorAll(".page");
            allPages.forEach(function(page) {
                page.classList.remove("active");
            });

            // Step 2: Remove "active" from ALL nav buttons
            const allBtns = document.querySelectorAll(".nav-btn");
            allBtns.forEach(function(btn) {
                btn.classList.remove("active");
            });

            // Step 3: Show only the history page
            document.getElementById("page-history").classList.add("active");

            // Step 4: Find and mark History button as active
            let historyBtn = null;
            for (let btn of allBtns) {
                if (btn.textContent.trim() === "History") {
                    historyBtn = btn;
                    break;
                }
            }
            if (historyBtn) {
                historyBtn.classList.add("active");
            }

            // Step 5: Load expenses
            loadExpenses();
            
        } else if (response.status === 404) {
            alert("Expense not found. It may have already been deleted.");
        } else {
            alert("Could not delete. Please try again.");
        }

    } catch (error) {
        alert("Cannot connect to Flask. Is it running?");
    }
}


// =====================================================
// 9. LOAD REPORTS (Charts page)
// Fetches analytics data and draws pie + bar charts
// =====================================================
async function loadReports() {
    try {
        const response = await fetch(`${API_URL}/api/analytics`);
        const result   = await response.json();
        const data     = result.data;

        // Update the 4 metric cards
        document.getElementById("rep-total").textContent     = "₹" + data.total_spent.toFixed(2);
        document.getElementById("rep-count").textContent     = data.total_expenses;
        document.getElementById("rep-anomalies").textContent = data.anomaly_count;

        const topCategory = data.category_totals.length > 0
            ? data.category_totals[0].category
            : "-";
        document.getElementById("rep-top-cat").textContent = topCategory;

        // Draw the two charts
        drawPieChart(data.category_totals);
        drawBarChart(data.monthly_totals);

    } catch (error) {
        console.error("Cannot load reports:", error);
    }
}


// =====================================================
// 10. DRAW PIE CHART
// Uses Chart.js to draw category spending breakdown
// =====================================================
function drawPieChart(categoryData) {
    const ctx = document.getElementById("pie-chart").getContext("2d");

    // Destroy old chart before drawing new one
    // (Otherwise Chart.js throws an error)
    if (pieChart) {
        pieChart.destroy();
    }

    if (categoryData.length === 0) {
        return;
    }

    // Extract labels (category names) and values (amounts)
    const labels = categoryData.map(function(c) { return c.category; });
    const values = categoryData.map(function(c) { return c.total; });
    const colors = labels.map(function(l) { return CATEGORY_COLORS[l] || "#888"; });

    pieChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: labels,
            datasets: [{
                data:            values,
                backgroundColor: colors,
                borderWidth:     2,
                borderColor:     "#ffffff"
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { font: { size: 12 } }
                },
                tooltip: {
                    callbacks: {
                        // Show rupee symbol in tooltip
                        label: function(context) {
                            return " ₹" + context.parsed.toFixed(2);
                        }
                    }
                }
            }
        }
    });
}


// =====================================================
// 11. DRAW BAR CHART
// Uses Chart.js to draw monthly spending trend
// =====================================================
function drawBarChart(monthlyData) {
    const ctx = document.getElementById("bar-chart").getContext("2d");

    // Destroy old chart before drawing new one
    if (barChart) {
        barChart.destroy();
    }

    if (monthlyData.length === 0) {
        return;
    }

    const labels = monthlyData.map(function(m) { return m.month; });
    const values = monthlyData.map(function(m) { return m.total; });

    barChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label:           "Total Spending (₹)",
                data:            values,
                backgroundColor: "#2A9D8F",
                borderRadius:    6
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        // Add rupee symbol to Y axis labels
                        callback: function(value) {
                            return "₹" + value;
                        }
                    }
                }
            }
        }
    });
}


// =====================================================
// 12. LOAD PREDICTION (Predictions page)
// Fetches forecast from Flask and displays it
// =====================================================
async function loadPrediction() {
    const amountEl = document.getElementById("pred-amount");
    const trendEl  = document.getElementById("pred-trend");
    const infoEl   = document.getElementById("pred-info");

    amountEl.textContent = "Loading...";
    trendEl.textContent  = "";
    infoEl.textContent   = "";

    try {
        const response = await fetch(`${API_URL}/api/forecast`);
        const result   = await response.json();
        const forecast = result.data;

        // Not enough data to forecast
        if (forecast.trend === "insufficient_data") {
            amountEl.textContent = "N/A";
            infoEl.textContent   = "Add expenses across at least 2 different months to see a prediction.";
            return;
        }

        // Show predicted amount
        amountEl.textContent = "₹" + forecast.predicted_amount.toFixed(0);

        // Show trend with different colors
        const trendMap = {
            "increasing": { text: "Trend: Spending is Rising",   color: "#E76F51" },
            "decreasing": { text: "Trend: Spending is Falling",  color: "#57CC99" },
            "stable":     { text: "Trend: Spending is Stable",   color: "#4895EF" }
        };

        const trendInfo = trendMap[forecast.trend] || { text: forecast.trend, color: "#888" };
        trendEl.textContent   = trendInfo.text;
        trendEl.style.color   = trendInfo.color;
        infoEl.textContent    = "Based on " + forecast.data_points + " month(s) of data";

    } catch (error) {
        amountEl.textContent = "Error";
        infoEl.textContent   = "Cannot load prediction. Is Flask running?";
    }
}


// =====================================================
// 13. LOAD TIPS / INSIGHTS (Tips page)
// Fetches insights from Flask and shows as tip cards
// =====================================================
async function loadTips() {
    const tipsEl = document.getElementById("tips-list");
    tipsEl.innerHTML = `<p class="loading">Loading tips...</p>`;

    try {
        const response = await fetch(`${API_URL}/api/insights`);
        const result   = await response.json();
        const insights = result.data;

        if (insights.length === 0) {
            tipsEl.innerHTML = `<p class="empty-state">No tips yet. Add more expenses to unlock spending insights.</p>`;
            return;
        }

        // Build tip cards
        let html = "";
        insights.forEach(function(tip) {
            // Remove emoji characters so text is clean
            const cleanTip = tip.replace(/[^\w\s₹%.,:()\-+!]/g, "").trim();
            html += `<div class="tip-card">${cleanTip}</div>`;
        });

        tipsEl.innerHTML = html;

    } catch (error) {
        tipsEl.innerHTML = `<p class="msg-error">Cannot load tips. Is Flask running?</p>`;
    }
}


// =====================================================
// 14. BUDGET FUNCTIONS (Budget page)
// Add, load, delete, and display budgets
// =====================================================

async function addBudgetForm() {
    const category = document.getElementById("budget-category").value;
    const amount   = document.getElementById("budget-amount").value;
    const period   = document.getElementById("budget-period").value;
    const messageEl = document.getElementById("budget-form-msg");

    console.log("Adding budget:", { category, amount, period });

    if (!category) {
        messageEl.innerHTML = `<div class="msg-error">Please select a category.</div>`;
        return;
    }
    if (!amount || Number(amount) <= 0) {
        messageEl.innerHTML = `<div class="msg-error">Please enter a valid amount.</div>`;
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/budgets`, {
            method:  "POST",
            headers: { "Content-Type": "application/json" },
            body:    JSON.stringify({
                category: category,
                amount:   parseFloat(amount),
                period:   period
            })
        });

        console.log("Add budget response status:", response.status);
        const result = await response.json();
        console.log("Add budget result:", result);

        if (response.status === 201) {
            // Success - budget added
            messageEl.innerHTML = `<div class="msg-success">Budget saved for ${category} (${period})!</div>`;
            
            // Clear the form
            document.getElementById("budget-amount").value = "";
            
            // Reload budget table
            loadBudgets();

        } else {
            messageEl.innerHTML = `<div class="msg-error">Error: ${result.message}</div>`;
        }

    } catch (error) {
        console.error("Error adding budget:", error);
        messageEl.innerHTML = `<div class="msg-error">Cannot connect to Flask. Is it running?</div>`;
    }
}


async function loadBudgets() {
    const tbody = document.getElementById("budget-tbody");
    tbody.innerHTML = `<tr><td colspan="8" class="loading">Loading budgets...</td></tr>`;

    try {
        console.log("Fetching budgets from:", `${API_URL}/api/budget-report`);
        const response = await fetch(`${API_URL}/api/budget-report`);
        console.log("Response status:", response.status);
        
        const result   = await response.json();
        console.log("Budget data:", result);
        const budgets  = result.data;

        if (budgets.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="empty-state">No budgets set. Create one above!</td></tr>`;
            return;
        }

        renderBudgetTable(budgets);

    } catch (error) {
        console.error("Error loading budgets:", error);
        tbody.innerHTML = `<tr><td colspan="8" class="msg-error">Error: ${error.message}</td></tr>`;
    }
}


function renderBudgetTable(budgets) {
    const tbody = document.getElementById("budget-tbody");
    let html = "";

    budgets.forEach(function(budget) {
        const statusClass = "status-" + budget.status;
        const statusText = {
            "good":    "✓ Good",
            "warning": "⚠ Warning",
            "over":    "✗ Over"
        }[budget.status] || budget.status;

        html += `
            <tr>
                <td><strong>${budget.category}</strong></td>
                <td>${budget.period}</td>
                <td>₹${budget.budget.toFixed(0)}</td>
                <td>₹${budget.spent.toFixed(2)}</td>
                <td>₹${budget.remaining.toFixed(2)}</td>
                <td>${budget.percentage}%</td>
                <td><span class="${statusClass}">${statusText}</span></td>
                <td>
                    <button class="btn-delete-budget" onclick="deleteBudget('${budget.category}', '${budget.period}')">
                        Delete
                    </button>
                </td>
            </tr>`;
    });

    tbody.innerHTML = html;
}


async function deleteBudget(category, period) {
    const confirmed = confirm(`Delete budget for ${category} (${period})?`);
    if (!confirmed) return;

    try {
        const response = await fetch(`${API_URL}/api/budgets/${category}/${period}`, {
            method: "DELETE"
        });

        if (response.status === 200) {
            // Step 1: Hide ALL pages
            const allPages = document.querySelectorAll(".page");
            allPages.forEach(function(page) {
                page.classList.remove("active");
            });

            // Step 2: Remove "active" from ALL nav buttons
            const allBtns = document.querySelectorAll(".nav-btn");
            allBtns.forEach(function(btn) {
                btn.classList.remove("active");
            });

            // Step 3: Show only the budget page
            document.getElementById("page-budget").classList.add("active");

            // Step 4: Find and mark Budget button as active
            let budgetBtn = null;
            for (let btn of allBtns) {
                if (btn.textContent.trim() === "Budget") {
                    budgetBtn = btn;
                    break;
                }
            }
            if (budgetBtn) {
                budgetBtn.classList.add("active");
            }

            // Step 5: Load budgets
            loadBudgets();
            
        } else {
            alert("Could not delete budget. Please try again.");
        }

    } catch (error) {
        alert("Cannot connect to Flask. Is it running?");
    }
}


// =====================================================
// 15. SET DEFAULT DATE
// Sets today's date as the default value in the date input
// =====================================================
function setDefaultDate() {
    const today = new Date().toISOString().split("T")[0]; // gives "2026-05-14"
    document.getElementById("input-date").value = today;
}


// =====================================================
// 16. RUNS WHEN THE PAGE FIRST LOADS
// window.onload waits for all HTML to be ready first
// =====================================================
window.onload = function() {
    checkBackendStatus(); // check if Flask is online
    setDefaultDate();     // set today's date in the form
};
