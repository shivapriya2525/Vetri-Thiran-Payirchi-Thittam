# Code-Layout, Readability and Reusability

| Team ID | Project Title | Team Size | Team Leader |
| --- | --- | --- | --- |
| SWTID-2026-9211 | PocketSmart AI: Your Smart Budget & Recommendation Assistant | 5 | Sivapriya S |

## Project Folder Layout

```
pocketsmart-ai/
├── app.py                 # Streamlit entry point
├── auth.py                # Registration and login
├── expenses.py            # Expense operations
├── classifier.py          # ML category model
├── budget.py              # Budget checks and alerts
├── anomaly.py             # Unusual spending detection
├── recommender.py         # Saving recommendations
├── assistant.py           # AI chat assistant
├── goals.py               # Savings goal planner
├── reports.py             # CSV report export
├── database.py            # SQLite connection and queries
├── data/
│   └── expense_training_data.csv
├── models/
│   └── category_model.pkl
├── requirements.txt
└── README.md
```

## Code Quality Practices

| S.No | Aspect | Practice Followed | Example |
| --- | --- | --- | --- |
| 1 | Layout | One module per feature with a clear single responsibility | `budget.py` handles only budget logic |
| 2 | Naming | Descriptive snake_case names for functions and variables | `predict_category`, `monthly_total` |
| 3 | Readability | Short functions, type hints and docstrings | `def budget_status(spent: float, limit: float) -> str` |
| 4 | Reusability | Shared helpers used by many screens | `database.py` used by expenses, goals and reports |
| 5 | Configuration | API keys and settings kept outside the code | `.env` file and environment variables |
| 6 | Error Handling | Validation of inputs and safe API calls | Reject negative amounts, handle API timeouts |
| 7 | Version Control | Feature-wise commits with clear messages | `feat: add budget alerts` |
| 8 | Dependencies | All libraries listed in one file | `requirements.txt` |
