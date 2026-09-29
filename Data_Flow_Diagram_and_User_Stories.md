# Data Flow Diagram & User Stories

| | |
|---|---|
| **Date** | 29/09/2026 |
| **Team ID** | SWTID-2026-9211 |
| **Project Name** | Pocket Smart AI – AI Budget Planner |
| **Team Size** | 5 |
| **Team Leader** | Sivapriya S |
| **Team Members** | Amala Merlin A, Anjali K, Balaharish, Bharanidharan R |

---

## Data Flow Diagram (Level 0)
```
[User] --(income, expenses, goals)--> [Pocket Smart AI System] --(dashboard, alerts, forecast, tips)--> [User]
```

## Data Flow Diagram (Level 1)
```
[User]
  |  expense details
  v
(1.0 Expense Entry) ----> [D1: Expenses Database]
  |                                |
  v                                v
(2.0 Auto-Categorise ML Model)   (3.0 Budget Check) <---- [D2: Budgets & Goals]
  |                                |
  v                                v
(4.0 Forecast Engine) -------> (5.0 Dashboard & Alerts) ----> [User]
```

## User Stories
| User Type | Story ID | As a... | I want to... | So that... | Priority |
|---|---|---|---|---|---|
| Student / Earner | US-1 | user | register and log in | my data stays private | High |
| Student / Earner | US-2 | user | set my monthly income and category budgets | I know how much I can spend | High |
| Student / Earner | US-3 | user | add an expense in a few taps | tracking is not boring | High |
| Student / Earner | US-4 | user | see my expense category suggested automatically | I save time | Medium |
| Student / Earner | US-5 | user | view charts of my spending | I understand my habits | High |
| Student / Earner | US-6 | user | get an alert before I cross a limit | I can control overspending | High |
| Student / Earner | US-7 | user | see a month-end spending forecast | I can plan ahead | Medium |
| Student / Earner | US-8 | user | set and track savings goals | I stay motivated to save | Medium |
| Student / Earner | US-9 | user | receive AI tips to cut expenses | I can save more | Low |
