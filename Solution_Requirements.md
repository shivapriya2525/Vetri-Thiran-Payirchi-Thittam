# Solution Requirements

| | |
|---|---|
| **Date** | 29/09/2026 |
| **Team ID** | SWTID-2026-9211 |
| **Project Name** | Pocket Smart AI – AI Budget Planner |
| **Team Size** | 5 |
| **Team Leader** | Sivapriya S |
| **Team Members** | Amala Merlin A, Anjali K, Balaharish, Bharanidharan R |

---

## Functional Requirements
| ID | Requirement | Description |
|---|---|---|
| FR-1 | User Registration and Login | Users register with email and password and log in securely |
| FR-2 | Income and Budget Setup | Users enter monthly income and set category-wise budget limits |
| FR-3 | Expense Entry | Users add, edit and delete expenses with amount, date, category and note |
| FR-4 | Auto-Categorisation | The system predicts a category from the expense description |
| FR-5 | Dashboard | Shows total spent, remaining budget and category-wise charts |
| FR-6 | Overspending Alerts | Notifies users when spending reaches 80% and 100% of a category limit |
| FR-7 | Spending Forecast | Predicts month-end spending from the current month's pattern |
| FR-8 | Savings Goals | Users create goals and track progress |
| FR-9 | AI Suggestions | Gives personalised tips to reduce spending |
| FR-10 | Reports | Monthly summary view of income, expenses and savings |

## Non-Functional Requirements
| ID | Requirement | Description |
|---|---|---|
| NFR-1 | Usability | Simple, mobile-friendly interface that a first-time user can use without training |
| NFR-2 | Security | Passwords stored hashed; financial data visible only to the owner |
| NFR-3 | Performance | Pages load within 3 seconds; prediction returns within 2 seconds |
| NFR-4 | Reliability | Data is saved immediately and the system runs with 99% availability during demo |
| NFR-5 | Scalability | Can support growth in users and expense records |
| NFR-6 | Accuracy | Auto-categorisation accuracy of at least 85% on test data |
| NFR-7 | Maintainability | Modular code with clear documentation |
