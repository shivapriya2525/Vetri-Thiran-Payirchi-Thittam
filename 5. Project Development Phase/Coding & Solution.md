# Coding & Solution

| Team ID | Project Title | Team Size | Team Leader |
| --- | --- | --- | --- |
| SWTID-2026-9211 | PocketSmart AI: Your Smart Budget & Recommendation Assistant | 5 | Sivapriya S |

## Feature Implementation Summary

| S.No | Module | Feature | Technology / File | Description |
| --- | --- | --- | --- | --- |
| 1 | Authentication | Register and login | `auth.py`, SQLite, hashlib | Stores users with hashed passwords and validates login |
| 2 | Expense Manager | Add, edit and view expenses | `expenses.py`, pandas | Saves amount, date, description and category |
| 3 | ML Categorisation | Automatic category prediction | `classifier.py`, scikit-learn | TF-IDF with Logistic Regression predicts category from description |
| 4 | Budget Manager | Category limits and alerts | `budget.py` | Compares monthly spend with limits and raises alerts at 80% and 100% |
| 5 | Anomaly Detection | Unusual spending detection | `anomaly.py`, Isolation Forest | Flags transactions far above the user's normal pattern |
| 6 | Recommendation Engine | Personalised saving tips | `recommender.py`, Generative AI API | Builds a prompt from spending summary and returns tips |
| 7 | AI Chat Assistant | Money Q&A | `assistant.py`, Generative AI API | Answers user questions using their transaction summary |
| 8 | Dashboard | Charts and insights | `app.py`, Plotly | Category pie chart, monthly trend and budget progress |
| 9 | Goal Planner | Savings goal tracking | `goals.py` | Calculates monthly saving needed and shows progress |
| 10 | Reports | CSV export | `reports.py`, pandas | Exports monthly summary |

## Feature 1: Automatic Expense Categorisation

| Item | Details |
| --- | --- |
| Input | Expense description, for example "Swiggy dinner order" |
| Model | TF-IDF Vectoriser + Logistic Regression |
| Output | Category such as Food, Travel, Shopping, Bills, Entertainment, Health, Education |

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline

model = make_pipeline(TfidfVectorizer(ngram_range=(1, 2)), LogisticRegression(max_iter=500))
model.fit(train_descriptions, train_categories)

def predict_category(description: str) -> str:
    return model.predict([description])[0]
```

## Feature 2: Budget Alert

| Item | Details |
| --- | --- |
| Input | Category limit and total spent in the month |
| Rule | Warning at 80% of limit, critical alert at 100% |
| Output | Alert message on the dashboard |

```python
def budget_status(spent: float, limit: float) -> str:
    ratio = spent / limit if limit else 0
    if ratio >= 1:
        return "Limit exceeded"
    if ratio >= 0.8:
        return "Nearing limit"
    return "Within budget"
```
