import os
import json
import re
import base64
import shutil
import urllib.parse
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union

from fastapi import (
    FastAPI, HTTPException, Depends, File, UploadFile,
    Form, Request, status, Cookie
)
from fastapi.responses import JSONResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

from models import (
    RegisterUser, UserLogin, UserInDB, Token, TokenData,
    UserSession, HomeBudgetInput, PartyBudgetInput, JewelryBudgetInput,
    RecommendationItem
)
import gemini_utils

load_dotenv()

# ==============================================================================
# Fast API App Initialization
# ==============================================================================
app = FastAPI(title="PocketSmart: AI Budget Planner")

SECRET_KEY = os.getenv("SECRET_KEY", "pocketsmart_ai_super_secret_jwt_key_2025")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ==============================================================================
# In-Memory & File-Backed Storage
# ==============================================================================
USERS_FILE = "data/users.json"
RECOMMENDATIONS_FILE = "data/recommendations.json"

active_sessions: Dict[str, UserSession] = {}
blacklisted_tokens: set = set()

def load_json_file(path: str, default: Any) -> Any:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default

def save_json_file(path: str, data: Any):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving {path}: {e}")

# Load or initialize users
raw_users = load_json_file(USERS_FILE, {})
users_db: Dict[str, UserInDB] = {}

# Seed default demo user 'sai' if not exists
if "sai" not in raw_users:
    default_hashed = pwd_context.hash("password123")
    raw_users["sai"] = {
        "username": "sai",
        "email": "sai@pocketsmart.ai",
        "full_name": "Sai Kumar",
        "hashed_password": default_hashed
    }
    save_json_file(USERS_FILE, raw_users)

for uname, udata in raw_users.items():
    users_db[uname] = UserInDB(**udata)

# Load recommendations
user_recommendations: Dict[str, List[dict]] = load_json_file(RECOMMENDATIONS_FILE, {})

# Seed sample recommendations for demo user 'sai' if empty
if "sai" not in user_recommendations or len(user_recommendations["sai"]) == 0:
    user_recommendations["sai"] = [
        {
            "id": "rec-demo-home-1",
            "timestamp": (datetime.now() - timedelta(days=2)).strftime("%B %d, %Y - %I:%M %p"),
            "type": "home",
            "title": "Home Budget Plan",
            "input_summary": {
                "budget": 5000.0,
                "rooms": "Living Room, Kitchen",
                "lights": 5,
                "fans": 4,
                "furniture": 2,
                "dining_tables": 1
            },
            "result_summary": {
                "total_budget": 5000.0,
                "remaining_budget": 500.0,
                "categories": ["Lighting", "Ceiling Fans", "Furniture"]
            },
            "full_result": {
                "total_budget": 5000.0,
                "remaining_budget": 500.0,
                "budget_breakdown": [
                    {
                        "category": "Lighting",
                        "allocation": 1500.0,
                        "items": [
                            {
                                "name": "LED Bulb (Warm White)",
                                "description": "Energy-efficient LED bulbs for general lighting.",
                                "price": 100.0,
                                "quantity": 5,
                                "shopping_links": {
                                    "amazon": "https://www.amazon.in/s?k=led+bulb+warm+white",
                                    "flipkart": "https://www.flipkart.com/search?q=led+bulb+warm+white",
                                    "ikea": "https://www.ikea.com/in/en/search/?q=led+bulb"
                                }
                            }
                        ]
                    }
                ],
                "calculation_table": [
                    {"category": "Lighting", "items_count": 5, "total_cost": 500.0, "percentage_of_budget": 10.0}
                ],
                "additional_suggestions": ["Consider purchasing energy-saving appliances."]
            }
        },
        {
            "id": "rec-demo-party-2",
            "timestamp": (datetime.now() - timedelta(days=1)).strftime("%B %d, %Y - %I:%M %p"),
            "type": "party",
            "title": "Birthday Party Budget Plan",
            "input_summary": {
                "budget": 5000.0,
                "party_type": "Birthday",
                "guests": 10,
                "venue": "Home"
            },
            "result_summary": {
                "total_budget": 5000.0,
                "remaining_budget": 0.0,
                "categories": ["Venue", "Catering", "Decoration", "Entertainment"]
            },
            "full_result": {
                "total_budget": 5000.0,
                "remaining_budget": 0.0,
                "budget_breakdown": [
                    {
                        "category": "Catering",
                        "allocation": 2500.0,
                        "items": [
                            {
                                "name": "Party Food Platters",
                                "description": "Tasty appetizers and party meals from Swiggy/Zomato.",
                                "price": 2500.0,
                                "quantity": 1,
                                "shopping_links": {
                                    "swiggy": "https://www.swiggy.com",
                                    "zomato": "https://www.zomato.com"
                                }
                            }
                        ]
                    }
                ],
                "venue_suggestions": [],
                "additional_suggestions": ["Order finger foods in bulk for maximum savings."]
            }
        },
        {
            "id": "rec-demo-jewelry-3",
            "timestamp": datetime.now().strftime("%B %d, %Y - %I:%M %p"),
            "type": "jewelry",
            "title": "Jewelry Budget Plan",
            "input_summary": {
                "budget": 5000.0,
                "occasion": "Anniversary",
                "preferences": "Minimalist silver"
            },
            "result_summary": {
                "total_budget": 5000.0,
                "remaining_budget": 800.0,
                "categories": ["Necklace", "Earrings", "Ring"]
            },
            "full_result": {
                "total_budget": 5000.0,
                "remaining_budget": 800.0,
                "jewelry_recommendations": [
                    {
                        "item_type": "Pendant Necklace",
                        "description": "925 Sterling Silver Solitaire Pendant",
                        "style": "Modern Minimalist",
                        "estimated_price": 2200.0,
                        "shopping_links": {
                            "caratlane": "https://www.caratlane.com",
                            "bluestone": "https://www.bluestone.com"
                        }
                    }
                ],
                "styling_tips": ["Wear with a V-neck dress for optimal balance."]
            }
        }
    ]
    save_json_file(RECOMMENDATIONS_FILE, user_recommendations)

# ==============================================================================
# Helper Functions: Auth & Sessions
# ==============================================================================
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def authenticate_user(username: str, password: str) -> Optional[UserInDB]:
    user = users_db.get(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_token(request: Request) -> Optional[str]:
    # Check Authorization header first
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header.split(" ")[1]
    # Check access_token cookie next
    token = request.cookies.get("access_token")
    if token:
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        return token
    return None

async def get_current_user(request: Request) -> Optional[UserInDB]:
    token = await get_token(request)
    if not token or token in blacklisted_tokens:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        user = users_db.get(username)
        if user is None:
            return None
        # Refresh last activity in session
        if username in active_sessions:
            active_sessions[username].last_activity = datetime.utcnow()
        return user
    except JWTError:
        return None

async def get_current_active_user(request: Request) -> UserInDB:
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in to continue.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

def save_to_history(username: str, recommendation_type: str, input_data: dict, result: dict):
    if username not in user_recommendations:
        user_recommendations[username] = []

    rec_id = f"rec-{uuid.uuid4().hex[:8]}"
    now_str = datetime.now().strftime("%B %d, %Y - %I:%M %p")

    title_map = {
        "home": "Home Interior Budget Plan",
        "party": f"{input_data.get('party_type', 'Party')} Budget Plan",
        "jewelry": f"{input_data.get('occasion', 'Jewelry')} Budget Plan"
    }

    # Extract clean result summary
    summary = {
        "total_budget": result.get("total_budget", input_data.get("total_budget", 0.0)),
        "remaining_budget": result.get("remaining_budget", 0.0),
        "items_count": len(result.get("jewelry_recommendations", [])) or len(result.get("budget_breakdown", []))
    }

    item = {
        "id": rec_id,
        "timestamp": now_str,
        "type": recommendation_type,
        "title": title_map.get(recommendation_type, "Budget Recommendation"),
        "input_summary": input_data,
        "result_summary": summary,
        "full_result": result
    }

    user_recommendations[username].insert(0, item)
    save_json_file(RECOMMENDATIONS_FILE, user_recommendations)
    return item

# ==============================================================================
# Startup Background Task: Clean Inactive Sessions
# ==============================================================================
@app.on_event("startup")
async def setup_session_cleanup():
    async def cleanup_expired_sessions():
        while True:
            current_time = datetime.utcnow()
            expired = [
                uname for uname, session in active_sessions.items()
                if (current_time - session.last_activity).total_seconds() > 1800
            ]
            for uname in expired:
                if uname in active_sessions:
                    print(f"Removing expired session for {uname}")
                    del active_sessions[uname]
            await asyncio.sleep(300)
    asyncio.create_task(cleanup_expired_sessions())

# ==============================================================================
# UI Routes: Authentication Pages & Actions
# ==============================================================================
@app.get("/", response_class=HTMLResponse)
async def landing_page(request: Request):
    """Main landing page introducing PocketSmart AI's features"""
    user = await get_current_user(request)
    return templates.TemplateResponse(request=request, name="index.html", context={"user": user})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page or redirect to dashboard if logged in"""
    token = await get_token(request)
    if token:
        user = await get_current_user(request)
        if user:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="login.html", context={})

@app.post("/login")
async def login_form_handler(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):
    """Form login handler"""
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={"error": "Invalid username or password", "username": username}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    active_sessions[user.username] = UserSession(
        username=user.username,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        token=token,
        user_data={}
    )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax"
    )
    return response

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """OAuth2 compatible token login endpoint"""
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    active_sessions[user.username] = UserSession(
        username=user.username,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        token=access_token,
        user_data={}
    )

    response = JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
    response.set_cookie(
        key="access_token",
        value=access_token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax"
    )
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    """Serve the registration page"""
    token = await get_token(request)
    if token:
        user = await get_current_user(request)
        if user:
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(request=request, name="register.html", context={})

@app.post("/register")
async def register_user(
    request: Request,
    username: str = Form(...),
    email: EmailStr = Form(...),
    full_name: Optional[str] = Form(None),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    """Register new user account"""
    if password != confirm_password:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": "Passwords do not match",
                "username": username,
                "email": email,
                "full_name": full_name
            }
        )

    if username in users_db:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={
                "error": f"Username '{username}' is already taken",
                "username": username,
                "email": email,
                "full_name": full_name
            }
        )

    hashed = get_password_hash(password)
    new_user = UserInDB(
        username=username,
        email=email,
        full_name=full_name or username,
        hashed_password=hashed
    )
    users_db[username] = new_user

    raw_users = load_json_file(USERS_FILE, {})
    raw_users[username] = new_user.dict()
    save_json_file(USERS_FILE, raw_users)

    # Automatically log the user in after registration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(data={"sub": username}, expires_delta=access_token_expires)
    active_sessions[username] = UserSession(
        username=username,
        login_time=datetime.utcnow(),
        last_activity=datetime.utcnow(),
        token=token,
        user_data={}
    )

    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key="access_token",
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        samesite="lax"
    )
    return response

@app.get("/logout")
@app.post("/logout")
async def logout(request: Request):
    """Terminates session, revokes token, redirects to login"""
    token = await get_token(request)
    if token:
        blacklisted_tokens.add(token)
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("sub")
            if username and username in active_sessions:
                del active_sessions[username]
        except JWTError:
            pass

    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="access_token")
    return response

# ==============================================================================
# Dashboard & History Pages
# ==============================================================================
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    """User dashboard displaying planners and recent activities"""
    history = user_recommendations.get(current_user.username, [])
    recent_activity = history[:5]
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": current_user, "recent_activity": recent_activity}
    )

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    """User's recommendation history page"""
    history = user_recommendations.get(current_user.username, [])
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"user": current_user, "history": history}
    )

# ==============================================================================
# Planner Pages & Recommendation Endpoints
# ==============================================================================

# --- 1. HOME INTERIOR PLANNER ---
@app.get("/home-planner", response_class=HTMLResponse)
async def home_planner_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    """Home interior budget planner page"""
    return templates.TemplateResponse(request=request, name="home_planner.html", context={"user": current_user})

@app.post("/home-budget")
@app.post("/generate-home")
async def plan_home_budget(
    request: Request,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate home interior recommendations"""
    # Handle either JSON or Form data
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        budget_input = HomeBudgetInput(**body)
    else:
        form = await request.form()
        budget_input = HomeBudgetInput(
            total_budget=float(form.get("total_budget", 5000)),
            num_lights=int(form.get("num_lights", 0)),
            num_fans=int(form.get("num_fans", 0)),
            num_furniture=int(form.get("num_furniture", 0)),
            num_dining_tables=int(form.get("num_dining_tables", 0)),
            has_living_room="has_living_room" in form or form.get("has_living_room") == "true",
            has_kitchen="has_kitchen" in form or form.get("has_kitchen") == "true",
            has_bedroom="has_bedroom" in form or form.get("has_bedroom") == "true",
            additional_requirements=form.get("additional_requirements") or "None"
        )

    # Store last budget planning in session data
    if current_user.username in active_sessions:
        active_sessions[current_user.username].user_data["last_home_budget"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "budget": budget_input.total_budget,
            "requirements": {
                "lights": budget_input.num_lights,
                "fans": budget_input.num_fans,
                "furniture": budget_input.num_furniture,
                "dining_tables": budget_input.num_dining_tables
            }
        }

    # Get recommendations
    try:
        result = gemini_utils.get_home_recommendations(budget_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating home recommendations: {str(e)}")

    # Save to history
    save_to_history(
        username=current_user.username,
        recommendation_type="home",
        input_data=budget_input.dict(),
        result=result
    )

    return result

# --- 2. PARTY PLANNER ---
@app.get("/party-planner", response_class=HTMLResponse)
async def party_planner_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    """Party budget planner page"""
    return templates.TemplateResponse(request=request, name="party_planner.html", context={"user": current_user})

@app.post("/party-budget")
@app.post("/generate-party")
async def plan_party_budget(
    request: Request,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate party budget recommendations"""
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        budget_input = PartyBudgetInput(**body)
    else:
        form = await request.form()
        budget_input = PartyBudgetInput(
            total_budget=float(form.get("total_budget", 5000)),
            num_guests=int(form.get("num_guests", 10)),
            party_type=form.get("party_type", "Birthday"),
            venue_type=form.get("venue_type", "Home"),
            needs_catering="needs_catering" in form or form.get("needs_catering") == "true",
            needs_decoration="needs_decoration" in form or form.get("needs_decoration") == "true",
            needs_entertainment="needs_entertainment" in form or form.get("needs_entertainment") == "true",
            additional_requirements=form.get("additional_requirements") or "None"
        )

    # Store last budget planning in session data
    if current_user.username in active_sessions:
        active_sessions[current_user.username].user_data["last_party_budget"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "budget": budget_input.total_budget,
            "party_type": budget_input.party_type,
            "guests": budget_input.num_guests
        }

    # Get recommendations
    try:
        result = gemini_utils.get_party_recommendations(budget_input)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating party recommendations: {str(e)}")

    # Save to history
    save_to_history(
        username=current_user.username,
        recommendation_type="party",
        input_data=budget_input.dict(),
        result=result
    )

    return result

# --- 3. JEWELRY PLANNER (WITH MULTIMODAL IMAGE UPLOAD) ---
@app.get("/jewelry-planner", response_class=HTMLResponse)
async def jewelry_planner_page(request: Request, current_user: UserInDB = Depends(get_current_active_user)):
    """Jewelry budget planner page"""
    return templates.TemplateResponse(request=request, name="jewelry_planner.html", context={"user": current_user})

@app.post("/jewelry-budget")
@app.post("/generate-jewelry")
async def plan_jewelry_budget(
    request: Request,
    total_budget: float = Form(...),
    occasion: str = Form(...),
    preferences: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Generate jewelry budget recommendations with optional outfit image analysis"""
    budget_input = JewelryBudgetInput(
        total_budget=total_budget,
        occasion=occasion,
        preferences=preferences or "Modern elegant"
    )

    image_path = None
    image_filename = None
    if image and image.filename:
        # Save uploaded image to static/uploads
        ext = os.path.splitext(image.filename)[1] or ".jpg"
        unique_name = f"{uuid.uuid4().hex[:10]}{ext}"
        target_path = os.path.join("static", "uploads", unique_name)
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_path = target_path
        image_filename = f"/static/uploads/{unique_name}"

    # Store in session data
    if current_user.username in active_sessions:
        active_sessions[current_user.username].user_data["last_jewelry_budget"] = {
            "timestamp": datetime.utcnow().isoformat(),
            "budget": budget_input.total_budget,
            "occasion": budget_input.occasion,
            "has_image": image_path is not None
        }

    # Get recommendations
    try:
        result = gemini_utils.get_jewelry_recommendations(budget_input, image_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating jewelry recommendations: {str(e)}")

    if image_filename:
        result["uploaded_image_url"] = image_filename

    # Save to history
    input_data = budget_input.dict()
    if image_filename:
        input_data["image"] = image_filename

    save_to_history(
        username=current_user.username,
        recommendation_type="jewelry",
        input_data=input_data,
        result=result
    )

    return result

# ==============================================================================
# History & Session APIs
# ==============================================================================
@app.get("/recommendation-history")
async def get_recommendation_history(current_user: UserInDB = Depends(get_current_active_user)):
    """Get the user's recommendation history"""
    history = user_recommendations.get(current_user.username, [])
    return {"history": history}

@app.get("/recommendation-details/{recommendation_id}")
async def get_recommendation_details(
    recommendation_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get the full details of a specific past recommendation"""
    user_history = user_recommendations.get(current_user.username, [])
    for item in user_history:
        if item.get("id") == recommendation_id:
            return item
    raise HTTPException(status_code=404, detail="Recommendation not found")

@app.get("/session-info")
async def get_session_info(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user's session information"""
    if current_user.username in active_sessions:
        session = active_sessions[current_user.username]
        duration = int((datetime.utcnow() - session.login_time).total_seconds() // 60)
        return {
            "username": session.username,
            "login_time": session.login_time.isoformat(),
            "last_activity": session.last_activity.isoformat(),
            "session_duration_minutes": duration,
            "user_data": session.user_data
        }
    return {
        "username": current_user.username,
        "email": current_user.email,
        "status": "Active"
    }

@app.post("/session-data")
async def update_session_data(
    data: Dict[str, Any],
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update user's session data"""
    if current_user.username in active_sessions:
        active_sessions[current_user.username].user_data.update(data)
        active_sessions[current_user.username].last_activity = datetime.utcnow()
        return {
            "message": "Session data updated",
            "data": active_sessions[current_user.username].user_data
        }
    raise HTTPException(status_code=404, detail="No active session found")

# ==============================================================================
# Main Entry Point
# ==============================================================================
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")
    print(f"Starting PocketSmart: AI Budget Planner on http://localhost:{port}...")
    uvicorn.run("app:app", host=host, port=port, reload=True)
