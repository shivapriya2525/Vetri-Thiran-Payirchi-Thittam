# Pocket Smart AI – Development Guide

| | |
|---|---|
| **Date** | 29/09/2026 |
| **Team ID** | SWTID-2026-9211 |
| **Project Name** | Pocket Smart AI – AI Budget Planner |
| **Team Size** | 5 |
| **Team Leader** | Sivapriya S |
| **Team Members** | Amala Merlin A, Anjali K, Balaharish, Bharanidharan R |

---

## Modules Developed
1. Authentication (register / login)
2. Budget and income setup
3. Expense management
4. ML auto-categorisation (`model_training.py`)
5. Spending forecast
6. Dashboard and alerts (`app.py`)

## How to Run
```bash
pip install -r requirements.txt
python model_training.py     # trains and saves category_model.pkl
python app.py                # starts the app at http://127.0.0.1:5000
```

## Folder Contents
| File | Purpose |
|---|---|
| `app.py` | Flask backend with expense, budget summary, forecast and alert APIs |
| `model_training.py` | Trains the expense category classifier |
| `requirements.txt` | Python dependencies |
