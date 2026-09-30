# Project Executable Files

| Team ID | Project Title | Team Size | Team Leader |
| --- | --- | --- | --- |
| SWTID-2026-9211 | PocketSmart AI: Your Smart Budget & Recommendation Assistant | 5 | Sivapriya S |

## Executable Files

| S.No | File Name | Type | Purpose |
| --- | --- | --- | --- |
| 1 | `app.py` | Python (Streamlit) | Main application; run this file to start PocketSmart AI |
| 2 | `database.py` | Python | Creates the SQLite database and tables |
| 3 | `classifier.py` | Python | Trains and loads the expense category model |
| 4 | `models/category_model.pkl` | Model file | Saved trained classifier |
| 5 | `data/expense_training_data.csv` | Dataset | Labelled expense descriptions for training |
| 6 | `requirements.txt` | Text | List of required Python libraries |
| 7 | `.env` | Configuration | Stores the Generative AI API key |

## How to Run

| Step | Command | Description |
| --- | --- | --- |
| 1 | `pip install -r requirements.txt` | Install dependencies |
| 2 | `python classifier.py` | Train the category model (first run only) |
| 3 | `streamlit run app.py` | Launch the application in the browser |
