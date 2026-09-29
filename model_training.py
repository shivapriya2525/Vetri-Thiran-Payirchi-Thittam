# Pocket Smart AI - Expense Category Model
# Team ID: SWTID-2026-9211 | Date: 29/09/2026
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

data = [
    ("swiggy dinner", "Food"), ("zomato lunch order", "Food"), ("grocery store", "Food"),
    ("tea and snacks", "Food"), ("bus ticket", "Transport"), ("metro recharge", "Transport"),
    ("uber ride", "Transport"), ("petrol", "Transport"), ("netflix subscription", "Entertainment"),
    ("movie tickets", "Entertainment"), ("spotify", "Entertainment"), ("electricity bill", "Bills"),
    ("mobile recharge", "Bills"), ("wifi bill", "Bills"), ("water bill", "Bills"),
    ("new shirt", "Shopping"), ("amazon order", "Shopping"), ("shoes", "Shopping"),
    ("college fees", "Education"), ("books", "Education"), ("course fee", "Education"),
    ("medicine", "Health"), ("doctor consultation", "Health"), ("gym membership", "Health"),
]
texts, labels = zip(*data)
model = make_pipeline(TfidfVectorizer(), MultinomialNB())
model.fit(texts, labels)
joblib.dump(model, "category_model.pkl")
print("Model trained. Test:", model.predict(["dominos pizza"])[0])
