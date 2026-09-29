# Pocket Smart AI - Flask Backend
# Team ID: SWTID-2026-9211 | Date: 29/09/2026
import sqlite3, datetime, calendar, joblib
from flask import Flask, request, jsonify

app = Flask(__name__)
DB = "pocket_smart_ai.db"
model = joblib.load("category_model.pkl")

def db():
    con = sqlite3.connect(DB); con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("CREATE TABLE IF NOT EXISTS expenses(id INTEGER PRIMARY KEY, amount REAL, category TEXT, note TEXT, date TEXT)")
        con.execute("CREATE TABLE IF NOT EXISTS budgets(category TEXT PRIMARY KEY, limit_amount REAL)")

@app.route("/expense", methods=["POST"])
def add_expense():
    d = request.json
    category = d.get("category") or model.predict([d["note"]])[0]
    date = d.get("date") or datetime.date.today().strftime("%d/%m/%Y")
    with db() as con:
        con.execute("INSERT INTO expenses(amount,category,note,date) VALUES(?,?,?,?)", (d["amount"], category, d["note"], date))
    return jsonify({"message": "Expense added", "category": category}), 201

@app.route("/budget", methods=["POST"])
def set_budget():
    d = request.json
    with db() as con:
        con.execute("REPLACE INTO budgets VALUES(?,?)", (d["category"], d["limit"]))
    return jsonify({"message": "Budget saved"})

@app.route("/summary")
def summary():
    with db() as con:
        spent = {r["category"]: r["t"] for r in con.execute("SELECT category, SUM(amount) t FROM expenses GROUP BY category")}
        limits = {r["category"]: r["limit_amount"] for r in con.execute("SELECT * FROM budgets")}
    alerts = [f"{c}: {spent.get(c,0)/l*100:.0f}% of budget used" for c, l in limits.items() if spent.get(c, 0) >= 0.8 * l]
    return jsonify({"spent": spent, "limits": limits, "alerts": alerts})

@app.route("/forecast")
def forecast():
    today = datetime.date.today()
    days_in_month = calendar.monthrange(today.year, today.month)[1]
    with db() as con:
        total = con.execute("SELECT COALESCE(SUM(amount),0) FROM expenses").fetchone()[0]
    predicted = round(total / max(today.day, 1) * days_in_month, 2)
    return jsonify({"spent_so_far": total, "predicted_month_end": predicted})

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
