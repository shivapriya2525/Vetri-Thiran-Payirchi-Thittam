# Functional Test Cases

| | |
|---|---|
| **Date** | 29/09/2026 |
| **Team ID** | SWTID-2026-9211 |
| **Project Name** | Pocket Smart AI – AI Budget Planner |
| **Team Size** | 5 |
| **Team Leader** | Sivapriya S |
| **Team Members** | Amala Merlin A, Anjali K, Balaharish, Bharanidharan R |

---

| Test Case ID | Module | Scenario | Test Steps | Expected Result | Status |
|---|---|---|---|---|---|
| TC-01 | Authentication | Valid registration | Enter valid name, email, password and submit | Account created, user redirected to login | Pass |
| TC-02 | Authentication | Login with wrong password | Enter correct email and wrong password | Error message shown, access denied | Pass |
| TC-03 | Budget | Set category budget | Enter Food limit of 3000 and save | Budget saved and shown on dashboard | Pass |
| TC-04 | Expense | Add valid expense | Enter amount 250 and note "swiggy dinner" | Expense saved with category Food | Pass |
| TC-05 | Expense | Add expense with empty amount | Leave amount blank and submit | Validation error displayed | Pass |
| TC-06 | ML Model | Auto-categorise | Note "uber ride" | Category predicted as Transport | Pass |
| TC-07 | Alert | 80% budget reached | Add expenses totalling 80% of a limit | Alert message displayed | Pass |
| TC-08 | Forecast | Month-end prediction | Open forecast after several entries | Predicted month-end amount displayed | Pass |
| TC-09 | Dashboard | Category chart | Open dashboard after adding expenses | Chart matches stored data | Pass |
| TC-10 | Goals | Create savings goal | Enter goal name, target and date | Goal created with progress bar | Pass |
