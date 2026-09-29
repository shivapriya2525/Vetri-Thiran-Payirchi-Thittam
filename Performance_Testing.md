# Performance Testing

| | |
|---|---|
| **Date** | 29/09/2026 |
| **Team ID** | SWTID-2026-9211 |
| **Project Name** | Pocket Smart AI – AI Budget Planner |
| **Team Size** | 5 |
| **Team Leader** | Sivapriya S |
| **Team Members** | Amala Merlin A, Anjali K, Balaharish, Bharanidharan R |

---

| S.No. | Parameter | Values | Screenshot / Result |
|---|---|---|---|
| 1 | **Model Summary** | Multinomial Naive Bayes with TF-IDF for category prediction; linear projection for month-end forecast | Model trained and saved as `category_model.pkl` |
| 2 | **Accuracy** | Target ≥ 85% on held-out expense descriptions | Meets target on test set |
| 3 | **Response Time** | Expense API under 1 second; forecast under 2 seconds | Within limits |
| 4 | **Page Load Time** | Dashboard loads within 3 seconds | Within limits |
| 5 | **Concurrent Users** | Tested with 20 simulated users | No failures |
| 6 | **Data Validation** | Invalid or empty inputs rejected | Verified |
