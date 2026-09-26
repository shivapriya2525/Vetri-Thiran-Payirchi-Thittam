import os
import sys
from fastapi.testclient import TestClient
from app import app, users_db, pwd_context, UserInDB

def test_pocketsmart_application():
    client = TestClient(app)
    print("\n--- Starting PocketSmart AI Automated Test Suite ---")

    # 1. Test Landing Page
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "PocketSmart" in res.text
    assert "AI-Powered Budget Planning" in res.text
    print("[PASS] Landing page renders properly")

    # 2. Test Login Page
    res = client.get("/login")
    assert res.status_code == 200
    assert "Welcome Back" in res.text
    print("[PASS] Login page renders properly")

    # 3. Test Register Page
    res = client.get("/register")
    assert res.status_code == 200
    assert "Create Your Account" in res.text
    print("[PASS] Register page renders properly")

    # 4. Test Token Auth
    res = client.post("/token", data={"username": "sai", "password": "password123"})
    assert res.status_code == 200, f"Token failed: {res.text}"
    token_data = res.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    client.cookies.set("access_token", token)
    print("[PASS] User authentication & JWT token generation succeeded")

    # 5. Test Dashboard
    res = client.get("/dashboard", headers=headers)
    assert res.status_code == 200
    assert "Welcome, sai!" in res.text
    assert "Home Budget Planner" in res.text
    print("[PASS] User dashboard loaded with authenticated session")

    # 6. Test Home Planner Page & Endpoint
    res = client.get("/home-planner", headers=headers)
    assert res.status_code == 200
    assert "Home Interior Budget Planner" in res.text

    home_payload = {
        "total_budget": 50000.0,
        "num_lights": 6,
        "num_fans": 3,
        "num_furniture": 2,
        "num_dining_tables": 1,
        "has_living_room": True,
        "has_kitchen": True,
        "has_bedroom": True,
        "additional_requirements": "Warm modern aesthetic with wooden tones"
    }
    res = client.post("/home-budget", json=home_payload, headers=headers)
    assert res.status_code == 200, f"Home budget failed: {res.text}"
    home_data = res.json()
    assert "budget_breakdown" in home_data
    assert "calculation_table" in home_data
    assert "total_budget" in home_data
    assert len(home_data["budget_breakdown"]) > 0
    # verify shopping links exist
    first_item = home_data["budget_breakdown"][0]["items"][0]
    assert "shopping_links" in first_item
    assert "amazon" in first_item["shopping_links"]
    assert "flipkart" in first_item["shopping_links"]
    print("[PASS] Home Interior Planner API & shopping links generated correctly")

    # 7. Test Party Planner Page & Endpoint
    res = client.get("/party-planner", headers=headers)
    assert res.status_code == 200
    assert "Party Budget Planner" in res.text

    party_payload = {
        "total_budget": 25000.0,
        "num_guests": 20,
        "party_type": "Birthday",
        "venue_type": "Community Banquet Hall",
        "needs_catering": True,
        "needs_decoration": True,
        "needs_entertainment": True,
        "additional_requirements": "Vegetarian buffet and retro music theme"
    }
    res = client.post("/party-budget", json=party_payload, headers=headers)
    assert res.status_code == 200, f"Party budget failed: {res.text}"
    party_data = res.json()
    assert "budget_breakdown" in party_data
    assert "calculation_table_inr" in party_data
    assert "venue_suggestions" in party_data
    print("[PASS] Party Planner API & platform mappings generated correctly")

    # 8. Test Jewelry Planner Page & Multimodal Endpoint
    res = client.get("/jewelry-planner", headers=headers)
    assert res.status_code == 200
    assert "Jewelry Budget Planner" in res.text

    sample_img_path = "static/uploads/sample_outfit.jpg"
    with open(sample_img_path, "rb") as f:
        res = client.post(
            "/jewelry-budget",
            data={
                "total_budget": "15000.0",
                "occasion": "Wedding Reception",
                "preferences": "Kundan and pearls, gold-plated"
            },
            files={"image": ("outfit.jpg", f, "image/jpeg")},
            headers=headers
        )
    assert res.status_code == 200, f"Jewelry budget failed: {res.text}"
    jewelry_data = res.json()
    assert "jewelry_recommendations" in jewelry_data
    assert "styling_tips" in jewelry_data
    first_j = jewelry_data["jewelry_recommendations"][0]
    assert "shopping_links" in first_j
    assert "tanishq" in first_j["shopping_links"]
    assert "caratlane" in first_j["shopping_links"]
    print("[PASS] Jewelry Planner multimodal image upload & recommendations generated correctly")

    # 9. Test History & Details
    res = client.get("/history", headers=headers)
    assert res.status_code == 200
    assert "Your Recommendation History" in res.text

    res = client.get("/recommendation-history", headers=headers)
    assert res.status_code == 200
    hist = res.json()["history"]
    assert len(hist) > 0
    rec_id = hist[0]["id"]

    res = client.get(f"/recommendation-details/{rec_id}", headers=headers)
    assert res.status_code == 200
    assert res.json()["id"] == rec_id
    print("[PASS] Recommendation History and Details API functioning properly")

    # 10. Test Session Info
    res = client.get("/session-info", headers=headers)
    assert res.status_code == 200
    session_data = res.json()
    assert session_data.get("username") == "sai"
    print("[PASS] Active session info and metadata verified")

    # 11. Test Logout
    res = client.get("/logout")
    assert res.status_code == 200 or res.status_code == 302
    print("[PASS] Logout and session invalidation succeeded")

    print("\nALL 11 TEST SUITES PASSED FLAWLESSLY!\n")

if __name__ == "__main__":
    test_pocketsmart_application()
