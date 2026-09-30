# Performance Testing

| Team ID | Project Title | Team Size | Team Leader |
| --- | --- | --- | --- |
| SWTID-2026-9211 | PocketSmart AI: Your Smart Budget & Recommendation Assistant | 5 | Sivapriya S |

## Performance Testing

| S.No | Parameter | Values |
| --- | --- | --- |
| 1 | Model Summary | TF-IDF + Logistic Regression for expense category prediction (7 categories); Isolation Forest for anomaly detection |
| 2 | Training Data | Labelled expense descriptions split 80% training and 20% testing |
| 3 | Accuracy | Classification accuracy of 90% or above on the test split |
| 4 | Precision / Recall / F1-Score | 0.88 or above (weighted average) |
| 5 | Fine-Tuning Applied | TF-IDF n-gram range and Logistic Regression regularisation (C) tuned using cross-validation |
| 6 | Category Prediction Time | Under 1 second per expense |
| 7 | Dashboard Load Time | Under 3 seconds for one month of data |
| 8 | AI Assistant Response Time | Under 8 seconds per question |
| 9 | Concurrent Users Supported | 10 users on the demo setup |
| 10 | Error Handling | Invalid amounts, empty descriptions and API failures show friendly messages |
