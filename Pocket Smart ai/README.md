# PocketSmart AI: Your Smart Budget & Recommendation Assistant

PocketSmart AI is an intelligent, full-stack GenAI-powered web application that delivers personalized, budget-based suggestions across home interiors, party planning, and jewelry purchases. It integrates a high-performance **FastAPI** backend with **Google Gemini 1.5 Flash Pro** foundation model and a modern, responsive HTML/CSS/JavaScript interface.

---

## 🌟 Key Features & Scenarios

### 1. Home Interior Planning with Smart Budget Allocation
- **Input Parameters**: Total budget (INR), room selections (Living Room, Kitchen, Bedroom), quantities for lighting fixtures, ceiling fans, furniture pieces, dining tables, and custom requirements.
- **AI Recommendation Engine**: Calculates balanced allocations, remaining budget, and item costs.
- **E-Commerce Integration**: Provides direct, clickable search badges for **IKEA**, **Amazon**, **Flipkart**, **Myntra**, and **Ajio**.
- **Financial Breakdown**: Comprehensive calculation table showing item counts, category totals, and budget percentage allocations.

### 2. AI-Based Party Budget Planning
- **Input Parameters**: Total budget, number of guests, party type (Birthday, Wedding, Anniversary, Corporate, Dinner), venue type (Home, Banquet Hall, Rooftop, Resort, Restaurant), and service checkboxes (Catering, Decoration, Entertainment).
- **Service Allocation**: Proportional distribution across food & catering, venue booking, decor kits, entertainment systems, and contingency buffers.
- **Vendor & Booking Links**: Sourcing links for **Swiggy**, **Zomato**, **BigBasket**, **BookMyShow**, **OYO Rooms**, **Booking.com**, **MakeMyTrip**, **NoBroker**, **Amazon**, **Flipkart**, and **Meesho**.
- **Venue Suggestions**: Suggested venue types with guest capacities and estimated costs.

### 3. Jewelry Recommendations for Occasions (Multimodal Vision)
- **Input Parameters**: Total budget, occasion (Wedding, Birthday, Anniversary, Festive Puja), style preferences, and **optional outfit image upload**.
- **Multimodal AI Vision**: Analyzes uploaded outfit photos to extract detected colors, fashion style, and formality level.
- **Jewelry Sourcing**: Style-matched items (necklaces, earrings, bangles, rings, watches) linked directly to leading Indian jewelry platforms: **Tanishq**, **CaratLane**, **BlueStone**, **Melorra**, **Amazon**, **Flipkart**, and **Meesho**.
- **Styling Advice**: Actionable styling and pairing tips tailored to the occasion.

---

## 🛠️ Architecture & Tech Stack

- **Backend**: FastAPI (Python 3.12)
- **AI Foundation Model**: Google Gemini 1.5 Flash / Flash Pro (`google.generativeai`)
- **Authentication**: JWT (JSON Web Tokens), OAuth2 password flow, `passlib` bcrypt hashing, session cookies
- **Session Management**: Active sessions tracking with automated background cleanup of inactive sessions (> 30 mins)
- **Frontend**: HTML5, Vanilla CSS3 (custom design system), Jinja2 Templates, FontAwesome Icons
- **Storage**: Persistent JSON file store (`data/users.json`, `data/recommendations.json`) with in-memory caching

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install fastapi uvicorn python-dotenv google-generativeai pillow python-jose[cryptography] passlib bcrypt==4.0.1 python-multipart email-validator httpx
```

### 2. Configure Environment Variables (`.env`)
To connect your Google Gemini API key:
1. Obtain an API key from [Google AI Studio](https://aistudio.google.com/).
2. Open `.env` and set:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: If no API key is set, PocketSmart AI automatically runs with its built-in realistic smart recommendation engine, allowing full offline usage and testing).*

### 3. Run the Application
```bash
python app.py
```
Or with Uvicorn:
```bash
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```
Open your browser and navigate to: **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

---

## 🔑 Default Demo Credentials
- **Username**: `sai`
- **Password**: `password123`
*(You can also click "Create Account" on the Register page to create your own account).*

---

## 🧪 Automated Testing
Run the comprehensive 11-step end-to-end test suite:
```bash
python test_app.py
```
All tests validate landing page rendering, auth flow, JWT issuance, session management, Home Planner, Party Planner, Jewelry Multimodal Planner, recommendation history, and logout.

---

## 📁 Project Directory Structure
```
Pocket Smart ai/
├── .env                         # API keys & configuration
├── app.py                       # FastAPI application & route controllers
├── models.py                    # Pydantic schemas for auth, inputs, & sessions
├── gemini_utils.py              # Gemini AI client, prompts, & vendor link generators
├── test_app.py                  # End-to-end automated test suite
├── README.md                    # Project documentation
├── data/
│   ├── users.json               # Persisted registered user records
│   └── recommendations.json     # Persisted recommendation history
├── static/
│   ├── styles.css               # Modern design system & vendor badges
│   └── uploads/                 # Uploaded outfit images & sample assets
│       └── sample_outfit.jpg
└── templates/
    ├── index.html               # Landing page with hero & planner cards
    ├── login.html               # User authentication sign-in page
    ├── register.html            # User account creation page
    ├── dashboard.html           # User dashboard with recent activity
    ├── home_planner.html        # Home interior budget planner & results
    ├── party_planner.html       # Party budget planner & results
    ├── jewelry_planner.html     # Jewelry planner with outfit upload & results
    └── history.html             # Recommendation history & detail viewer modal
```
