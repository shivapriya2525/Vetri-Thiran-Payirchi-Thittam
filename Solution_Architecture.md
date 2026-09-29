# Solution Architecture

| | |
|---|---|
| **Date** | 29/09/2026 |
| **Team ID** | SWTID-2026-9211 |
| **Project Name** | Pocket Smart AI – AI Budget Planner |
| **Team Size** | 5 |
| **Team Leader** | Sivapriya S |
| **Team Members** | Amala Merlin A, Anjali K, Balaharish, Bharanidharan R |

---

## Architecture Diagram
```
+---------------------+        HTTPS        +---------------------------+
|  User (Web/Mobile)  | <-----------------> |  Frontend (HTML/CSS/JS,   |
|                     |                     |  Bootstrap, Chart.js)     |
+---------------------+                     +-------------+-------------+
                                                          | REST API
                                            +-------------v-------------+
                                            |  Backend (Flask)          |
                                            |  Auth | Expense | Budget  |
                                            |  Goals | Alerts | Reports |
                                            +------+------------+-------+
                                                   |            |
                              +--------------------v--+     +---v---------------------+
                              |  Database (SQLite)    |     |  AI / ML Module         |
                              |  Users, Expenses,     |     |  Category Classifier    |
                              |  Budgets, Goals       |     |  Spending Forecast      |
                              +-----------------------+     |  Tip Generator (opt.)   |
                                                            +-------------------------+
```

## Components
1. **Presentation Layer:** Responsive pages for login, dashboard, expenses, budgets and goals.
2. **Application Layer:** Flask APIs handle validation, budget checks and alert logic.
3. **AI Layer:** A trained text classifier predicts the expense category; a regression model forecasts month-end spending.
4. **Data Layer:** Relational database stores users, expenses, budgets and goals.

## Data Flow Summary
User adds expense → backend validates → ML model suggests category → expense saved → budget check runs → dashboard updated and alert sent if a limit is near.
