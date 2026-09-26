import os
import json
import re
import urllib.parse
from typing import Optional, Dict, Any, List
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

from models import HomeBudgetInput, PartyBudgetInput, JewelryBudgetInput

load_dotenv()

# Configure Gemini API
API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
gemini_model = None

if API_KEY:
    try:
        genai.configure(api_key=API_KEY)
        # Using gemini-1.5-flash as specified in project documents
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
    except Exception as e:
        print(f"Warning: Failed to initialize Gemini API: {e}")
        gemini_model = None

def extract_json_from_response(text: str) -> dict:
    """Clean markdown backticks and parse JSON safely."""
    try:
        text = text.strip()
        # Look for ```json ... ``` or ``` ... ```
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
        return json.loads(text)
    except Exception as e:
        # Fallback regex search for JSON object between outermost brackets
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                pass
        raise ValueError(f"Could not parse valid JSON from AI response: {str(e)}")

# ==============================================================================
# 1. HOME INTERIOR RECOMMENDATIONS
# ==============================================================================
def get_home_recommendations(budget_input: HomeBudgetInput) -> dict:
    """Generate home interior recommendations within budget in INR for Indian market"""
    rooms_list = []
    if budget_input.has_living_room:
        rooms_list.append("- Living room")
    if budget_input.has_kitchen:
        rooms_list.append("- Kitchen")
    if budget_input.has_bedroom:
        rooms_list.append("- Bedroom")
    rooms_str = "\n".join(rooms_list) if rooms_list else "- General living areas"

    prompt = f"""
I need interior design product recommendations for a home in India with a total budget of ₹{budget_input.total_budget:.2f}.
Requirements:
- {budget_input.num_lights} lights/lighting fixtures
- {budget_input.num_fans} ceiling fans
- {budget_input.num_furniture} furniture pieces
- {budget_input.num_dining_tables} dining tables
Additional rooms to consider:
{rooms_str}

Additional requirements: {budget_input.additional_requirements or "None"}

Please provide a detailed budget breakdown with product recommendations **available in India**.
Use **Indian brands and pricing**. Include **search terms** suitable for Indian shopping platforms.

Format your response as JSON with the following structure:
{{
  "total_budget": {budget_input.total_budget:.2f},
  "budget_breakdown": [
    {{
      "category": "Lighting",
      "allocation": 0.0,
      "items": [
        {{
          "name": "Philips LED Smart Bulb",
          "description": "Energy-efficient 9W LED bulb with warm & cool light",
          "estimated_price": 500.0,
          "quantity": 2,
          "search_terms": "philips led bulb 9w"
        }}
      ]
    }}
  ],
  "calculation_table": [
    {{
      "category": "Lighting",
      "items_count": 2,
      "total_cost": 1000.0,
      "percentage_of_budget": 10.0
    }}
  ],
  "remaining_budget": 0.0,
  "additional_suggestions": [
    "Consider purchasing energy-saving BLDC fans for long term savings",
    "Look for festive combo discounts on major Indian marketplaces"
  ]
}}
Ensure total costs stay within budget. Include search terms for each item to find on shopping websites like Flipkart, Amazon India, IKEA.
"""

    result = None
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            result = extract_json_from_response(response.text)
        except Exception as e:
            print(f"Gemini API call failed, falling back to smart local engine: {e}")
            result = None

    if not result:
        result = _generate_fallback_home_recommendations(budget_input)

    # Attach shopping links for each item (Amazon, Flipkart, IKEA, Myntra, Ajio)
    if "budget_breakdown" in result:
        for category in result.get("budget_breakdown", []):
            for item in category.get("items", []):
                search_terms = item.get("search_terms") or item.get("name", "")
                if search_terms:
                    encoded = urllib.parse.quote_plus(search_terms)
                    item["shopping_links"] = {
                        "amazon": f"https://www.amazon.in/s?k={encoded}",
                        "flipkart": f"https://www.flipkart.com/search?q={encoded}",
                        "ikea": f"https://www.ikea.com/in/en/search/?q={encoded}",
                        "myntra": f"https://www.myntra.com/search?q={encoded}",
                        "ajio": f"https://www.ajio.com/search/?text={encoded}"
                    }

    # Ensure calculation_table is present and accurately computed
    total_spent = 0.0
    calc_table = []
    for cat in result.get("budget_breakdown", []):
        cat_name = cat.get("category", "General")
        items = cat.get("items", [])
        items_count = sum(item.get("quantity", 1) for item in items)
        cat_total = sum(item.get("estimated_price", 0) * item.get("quantity", 1) for item in items)
        total_spent += cat_total
        pct = (cat_total / budget_input.total_budget * 100) if budget_input.total_budget > 0 else 0
        calc_table.append({
            "category": cat_name,
            "items_count": items_count,
            "total_cost": round(cat_total, 2),
            "percentage_of_budget": round(pct, 1)
        })

    result["calculation_table"] = calc_table
    result["total_budget"] = budget_input.total_budget
    result["remaining_budget"] = max(0.0, round(budget_input.total_budget - total_spent, 2))
    return result

def _generate_fallback_home_recommendations(b: HomeBudgetInput) -> dict:
    """Realistic smart fallback for home interior planning"""
    total = b.total_budget
    breakdown = []
    
    # 1. Lighting
    lights_qty = max(1, b.num_lights)
    light_price = min(800.0, max(250.0, (total * 0.15) / lights_qty))
    lights_total = light_price * lights_qty
    breakdown.append({
        "category": "Lighting",
        "allocation": round(lights_total, 2),
        "items": [
            {
                "name": "Wipro / Philips Smart LED Batten & Bulbs",
                "description": "Warm & cool white flicker-free LED fixtures with eye safety technology",
                "estimated_price": round(light_price, 2),
                "quantity": lights_qty,
                "search_terms": "philips wipro led batten light ceiling"
            }
        ]
    })

    # 2. Ceiling Fans
    fans_qty = max(1, b.num_fans)
    fan_price = min(3500.0, max(1200.0, (total * 0.25) / fans_qty))
    fans_total = fan_price * fans_qty
    breakdown.append({
        "category": "Ceiling Fans",
        "allocation": round(fans_total, 2),
        "items": [
            {
                "name": "Havells / Atomberg BLDC Energy Saver Fan",
                "description": "High-speed 1200mm sweep 5-star energy saving ceiling fan with remote control",
                "estimated_price": round(fan_price, 2),
                "quantity": fans_qty,
                "search_terms": "atomberg bldc ceiling fan 1200mm"
            }
        ]
    })

    # 3. Furniture
    furn_qty = max(1, b.num_furniture)
    furn_price = min(8000.0, max(1500.0, (total * 0.35) / furn_qty))
    furn_total = furn_price * furn_qty
    breakdown.append({
        "category": "Furniture",
        "allocation": round(furn_total, 2),
        "items": [
            {
                "name": "Modern Engineered Wood Coffee Table & Accent Chairs",
                "description": "Ergonomic, space-saving furniture set tailored for cozy living spaces",
                "estimated_price": round(furn_price, 2),
                "quantity": furn_qty,
                "search_terms": "modern wooden accent chair coffee table"
            }
        ]
    })

    # 4. Dining Table if specified
    if b.num_dining_tables > 0:
        dt_qty = b.num_dining_tables
        dt_price = min(15000.0, max(4000.0, total * 0.20 / dt_qty))
        breakdown.append({
            "category": "Dining Furniture",
            "allocation": round(dt_price * dt_qty, 2),
            "items": [
                {
                    "name": "Solid Wood 4-Seater Compact Dining Table Set",
                    "description": "Contemporary finish durable dining table suitable for family dinners",
                    "estimated_price": round(dt_price, 2),
                    "quantity": dt_qty,
                    "search_terms": "compact 4 seater dining table set wood"
                }
            ]
        })

    return {
        "total_budget": total,
        "budget_breakdown": breakdown,
        "additional_suggestions": [
            "Opt for 5-star or BLDC motor appliances to cut monthly electricity costs significantly.",
            "Mix statement lighting with ambient strip lights for an expensive look on a smart budget.",
            "Compare prices on Amazon Great Indian Festival and Flipkart Big Billion Days for extra bank cashback.",
            "Consider modular multi-functional furniture with built-in storage for compact rooms."
        ]
    }

# ==============================================================================
# 2. PARTY BUDGET PLANNING RECOMMENDATIONS
# ==============================================================================
def get_party_recommendations(budget_input: PartyBudgetInput) -> dict:
    """Generate party planning recommendations within budget in INR for Indian market"""
    prompt = f"""
I need party planning recommendations for India with a total budget of ₹{budget_input.total_budget:.2f}.
Party details:
- Type: {budget_input.party_type}
- Number of guests: {budget_input.num_guests}
- Venue type: {budget_input.venue_type or "Not specified"}
- Catering needed: {"Yes" if budget_input.needs_catering else "No"}
- Decoration needed: {"Yes" if budget_input.needs_decoration else "No"}
- Entertainment needed: {"Yes" if budget_input.needs_entertainment else "No"}
Additional requirements: {budget_input.additional_requirements or "None"}

Please provide a detailed budget breakdown with specific recommendations available in India using INR prices.
Use Indian brands, services, and typical cost expectations.

Format your response as JSON with the following structure:
{{
  "total_budget": {budget_input.total_budget:.2f},
  "budget_breakdown": [
    {{
      "category": "venue",
      "allocation": 0.0,
      "items": [
        {{
          "name": "",
          "description": "",
          "estimated_price": 0.0,
          "quantity": 1,
          "search_terms": ""
        }}
      ]
    }}
  ],
  "venue_suggestions": [
    {{
      "name": "Cozy Community Hall / Rooftop Lounge",
      "type": "Residential / Indoor Banquet",
      "capacity": {budget_input.num_guests},
      "estimated_cost": 0.0,
      "search_terms": "party venue hall booking"
    }}
  ],
  "remaining_budget": 0.0,
  "additional_suggestions": [
    "Consider self-catering or potluck style if comfortable with guests",
    "Look for discounts or offers on streaming services or board games"
  ]
}}
Ensure all costs are in INR and total does not exceed the given budget.
Provide search terms suitable for Indian websites such as BookMyShow, Swiggy, Flipkart, etc.
"""

    result = None
    if gemini_model:
        try:
            response = gemini_model.generate_content(prompt)
            result = extract_json_from_response(response.text)
        except Exception as e:
            print(f"Gemini API call failed, falling back to smart party engine: {e}")
            result = None

    if not result:
        result = _generate_fallback_party_recommendations(budget_input)

    # Platforms mapping as documented in Activity 3.4 / Milestone 2
    category_platforms = {
        "venue": ["google", "booking", "makemytrip", "oyorooms", "nobroker"],
        "catering": ["swiggy", "zomato"],
        "food": ["swiggy", "zomato", "bigbasket", "amazon", "flipkart"],
        "drinks": ["swiggy", "zomato", "bigbasket", "amazon", "flipkart"],
        "decoration": ["amazon", "flipkart", "meesho", "myntra"],
        "entertainment": ["bookmyshow", "amazon", "flipkart"],
        "gifts": ["amazon", "flipkart", "myntra", "meesho"],
        "photography": ["google", "amazon", "flipkart"],
        "music": ["amazon", "flipkart", "bookmyshow"],
        "games": ["amazon", "flipkart"],
        "accessories": ["amazon", "flipkart", "myntra", "meesho"],
        "transportation": ["makemytrip", "google"],
        "return_gifts": ["amazon", "flipkart", "myntra", "meesho"],
        "contingency": ["amazon", "flipkart", "google"]
    }
    default_platforms = ["amazon", "flipkart", "google"]

    def _build_links_for_terms(platforms, terms):
        links = {}
        enc = urllib.parse.quote_plus(terms)
        for p in platforms:
            if p == "amazon":
                links["amazon"] = f"https://www.amazon.in/s?k={enc}"
            elif p == "flipkart":
                links["flipkart"] = f"https://www.flipkart.com/search?q={enc}"
            elif p == "bigbasket":
                links["bigbasket"] = f"https://www.bigbasket.com/ps/?q={enc}"
            elif p == "swiggy":
                links["swiggy"] = f"https://www.swiggy.com/search?query={enc}"
            elif p == "zomato":
                links["zomato"] = f"https://www.zomato.com/search?q={enc}"
            elif p == "bookmyshow":
                links["bookmyshow"] = f"https://in.bookmyshow.com/search?q={enc}"
            elif p == "myntra":
                links["myntra"] = f"https://www.myntra.com/search?q={enc}"
            elif p == "meesho":
                links["meesho"] = f"https://www.meesho.com/search?q={enc}"
            elif p == "google":
                links["google"] = f"https://www.google.com/search?q={enc}"
            elif p == "booking":
                links["booking"] = f"https://www.booking.com/search.html?ss={enc}"
            elif p == "makemytrip":
                links["makemytrip"] = f"https://www.makemytrip.com/hotels/hotel-listing/?searchText={enc}"
            elif p == "oyorooms":
                links["oyorooms"] = f"https://www.oyorooms.com/search/?location={enc}"
            elif p == "nobroker":
                links["nobroker"] = f"https://www.nobroker.in/property/search?searchTerm={enc}"
        return links

    # Process items in budget breakdown
    total_spent = 0.0
    categories_calc = {}

    for cat in result.get("budget_breakdown", []):
        raw_cat = cat.get("category", "misc").lower()
        # Find matching platforms
        platforms = category_platforms.get(raw_cat, default_platforms)

        cat_items = cat.get("items", [])
        for item in cat_items:
            price = float(item.get("estimated_price", 0))
            qty = int(item.get("quantity", 1))
            total_spent += price * qty
            st = item.get("search_terms") or item.get("name", "")
            if st:
                item["shopping_links"] = _build_links_for_terms(platforms, st)

        cat_total = sum(float(i.get("estimated_price", 0)) * int(i.get("quantity", 1)) for i in cat_items)
        categories_calc[cat.get("category", "Misc")] = {
            "category": cat.get("category", "Misc"),
            "items_count": len(cat_items),
            "total_cost": round(cat_total, 2),
            "percentage_of_budget": round((cat_total / budget_input.total_budget * 100) if budget_input.total_budget > 0 else 0, 1)
        }

    # Process venue suggestions
    venue_platforms = ["google", "booking", "makemytrip", "oyorooms", "nobroker"]
    for venue in result.get("venue_suggestions", []):
        st = venue.get("search_terms") or venue.get("name", "")
        if st:
            venue["search_links"] = _build_links_for_terms(venue_platforms, st)

    # Attach calculation_table_inr
    result["calculation_table_inr"] = list(categories_calc.values())
    result["total_budget"] = budget_input.total_budget
    result["remaining_budget"] = max(0.0, round(budget_input.total_budget - total_spent, 2))
    return result

def _generate_fallback_party_recommendations(b: PartyBudgetInput) -> dict:
    """Realistic smart fallback for party budget planning"""
    total = b.total_budget
    guests = max(1, b.num_guests)
    breakdown = []

    # 1. Venue
    venue_cost = 0.0 if "home" in b.venue_type.lower() else round(total * 0.20, 2)
    breakdown.append({
        "category": "venue",
        "allocation": venue_cost,
        "items": [
            {
                "name": f"{b.venue_type.title()} Arrangement",
                "description": f"Private celebration space configured for {guests} guests",
                "estimated_price": venue_cost,
                "quantity": 1,
                "search_terms": f"party hall venue {b.venue_type}"
            }
        ]
    })

    # 2. Catering
    if b.needs_catering:
        per_head = max(150.0, round((total * 0.45) / guests, 2))
        cat_total = round(per_head * guests, 2)
        breakdown.append({
            "category": "catering",
            "allocation": cat_total,
            "items": [
                {
                    "name": "Party Buffet & Refreshment Combo",
                    "description": f"Curated appetizers, mains, and beverage package for {guests} guests",
                    "estimated_price": cat_total,
                    "quantity": 1,
                    "search_terms": f"party catering bulk food {b.party_type}"
                }
            ]
        })

    # 3. Decoration
    if b.needs_decoration:
        decor_cost = round(total * 0.15, 2)
        breakdown.append({
            "category": "decoration",
            "allocation": decor_cost,
            "items": [
                {
                    "name": f"{b.party_type} Themed Balloon Arch & Banner Kit",
                    "description": "Eco-friendly balloons, LED fairy lights, backdrop foil curtains, and props",
                    "estimated_price": decor_cost,
                    "quantity": 1,
                    "search_terms": f"party decoration kit balloons {b.party_type}"
                }
            ]
        })

    # 4. Entertainment
    if b.needs_entertainment:
        ent_cost = round(total * 0.10, 2)
        breakdown.append({
            "category": "entertainment",
            "allocation": ent_cost,
            "items": [
                {
                    "name": "Bluetooth Party Speaker & Party Games Pack",
                    "description": "Portable high-bass music system with interactive card/board trivia games",
                    "estimated_price": ent_cost,
                    "quantity": 1,
                    "search_terms": "party games board games speaker"
                }
            ]
        })

    # 5. Contingency / Gifts
    contingency = round(total * 0.10, 2)
    breakdown.append({
        "category": "contingency",
        "allocation": contingency,
        "items": [
            {
                "name": "Emergency Cushion & Disposable Tableware",
                "description": "Last-minute supplies, extra ice, and reusable cutlery set",
                "estimated_price": contingency,
                "quantity": 1,
                "search_terms": "biodegradable disposable party tableware"
            }
        ]
    })

    return {
        "total_budget": total,
        "budget_breakdown": breakdown,
        "venue_suggestions": [
            {
                "name": f"{b.venue_type.title()} Event Suite",
                "type": "Indoor / Semi-outdoor",
                "capacity": guests + 5,
                "estimated_cost": venue_cost,
                "search_terms": f"event venue for {guests} guests"
            }
        ],
        "additional_suggestions": [
            "Use digital invitations (WhatsApp video invites) to eliminate printing expenses.",
            "Order finger foods and platters from Swiggy/Zomato bulk delivery for maximum savings.",
            "Create a collaborative Spotify playlist so all guests can queue their favorite party hits.",
            "Pick up a reusable photo booth backdrop with DIY ring light for memorable social snaps."
        ]
    }

# ==============================================================================
# 3. JEWELRY BUDGET PLANNING RECOMMENDATIONS (WITH MULTIMODAL VISION)
# ==============================================================================
def get_jewelry_recommendations(budget_input: JewelryBudgetInput, image_path: Optional[str] = None) -> dict:
    """Generate jewelry recommendations based on uploaded dress/outfit and budget in INR"""
    base_prompt = f"""
I need jewelry recommendations for India with a total budget of ₹{budget_input.total_budget:.2f}.
Occasion: {budget_input.occasion}
Preferences: {budget_input.preferences or "Not specified"}
Provide only India-relevant styles, availability, and price ranges in INR.
"""

    result = None
    has_image = bool(image_path and os.path.exists(image_path))

    if has_image:
        prompt = base_prompt + """
An image of the outfit is uploaded. Suggest jewelry that complements it, considering color, design, and occasion appropriateness.
Format the output as JSON:
{
  "outfit_analysis": {
    "colors": ["navy blue", "gold embroidery"],
    "style": "contemporary ethnic",
    "formality": "festive / semi-formal"
  },
  "total_budget": 0.0,
  "jewelry_recommendations": [
    {
      "item_type": "necklace",
      "description": "Kundan choker with matching teardrop pearls",
      "style": "traditional elegant",
      "estimated_price": 1500.0,
      "search_terms": "kundan choker necklace set gold plated"
    }
  ],
  "remaining_budget": 0.0,
  "styling_tips": [
    "Balance high necklines with drop earrings and skip the heavy necklace",
    "Pair warm gold tones with emerald green or ruby red accents"
  ]
}
Make sure prices are in INR and stay within budget.
Include Indian-friendly search terms for shopping.
"""
        if gemini_model:
            try:
                img = Image.open(image_path)
                response = gemini_model.generate_content([prompt, img])
                result = extract_json_from_response(response.text)
            except Exception as e:
                print(f"Gemini Vision call failed, falling back to smart jewelry engine: {e}")
                result = None
    else:
        prompt = base_prompt + """
Format the output as JSON:
{
  "total_budget": 0.0,
  "jewelry_recommendations": [
    {
      "item_type": "earrings",
      "description": "Sterling silver chandelier earrings with zircon stones",
      "style": "modern classic",
      "estimated_price": 1200.0,
      "search_terms": "sterling silver chandelier earrings"
    }
  ],
  "remaining_budget": 0.0,
  "styling_tips": [
    "Choose lightweight pieces for long evening events to stay comfortable",
    "Layer delicate chains for a sleek, contemporary look"
  ]
}
Keep prices in INR and relevant to Indian brands.
"""
        if gemini_model:
            try:
                response = gemini_model.generate_content(prompt)
                result = extract_json_from_response(response.text)
            except Exception as e:
                print(f"Gemini Text call failed, falling back to smart jewelry engine: {e}")
                result = None

    if not result:
        result = _generate_fallback_jewelry_recommendations(budget_input, has_image)

    # Attach shopping links (India-specific jewelry platforms)
    # Platforms: Amazon, Flipkart, BlueStone, Tanishq, CaratLane, Melorra, Meesho
    total_spent = 0.0
    for item in result.get("jewelry_recommendations", []):
        price = float(item.get("estimated_price", 0))
        total_spent += price
        search_terms = item.get("search_terms") or f"{item.get('style', '')} {item.get('item_type', 'jewelry')}"
        encoded = urllib.parse.quote_plus(search_terms.strip())
        item["shopping_links"] = {
            "amazon": f"https://www.amazon.in/s?k={encoded}",
            "flipkart": f"https://www.flipkart.com/search?q={encoded}",
            "bluestone": f"https://www.bluestone.com/search.html?query={encoded}",
            "tanishq": f"https://www.tanishq.co.in/search?q={encoded}",
            "caratlane": f"https://www.caratlane.com/search?q={encoded}",
            "melorra": f"https://www.melorra.com/search?q={encoded}",
            "meesho": f"https://www.meesho.com/search?q={encoded}"
        }

    result["total_budget"] = budget_input.total_budget
    result["remaining_budget"] = max(0.0, round(budget_input.total_budget - total_spent, 2))
    return result

def _generate_fallback_jewelry_recommendations(b: JewelryBudgetInput, has_image: bool) -> dict:
    """Realistic smart fallback for jewelry recommendations"""
    total = b.total_budget
    recs = []

    # If wedding/ethnic occasion
    is_traditional = any(k in b.occasion.lower() for k in ["wedding", "shaadi", "ethnic", "diwali", "puja", "festive"])
    
    if is_traditional:
        neck_price = round(total * 0.45, 2)
        earring_price = round(total * 0.30, 2)
        bangle_price = round(total * 0.20, 2)
        
        recs.append({
            "item_type": "Necklace Set",
            "description": f"Gold-plated Kundan & Meenakari Choker with matching Maang Tikka for {b.occasion}",
            "style": "Royal Heritage",
            "estimated_price": neck_price,
            "search_terms": f"kundan choker necklace set {b.preferences}"
        })
        recs.append({
            "item_type": "Jhumkas / Earrings",
            "description": "Handcrafted temple jewelry floral drop jhumkas with pearl tassels",
            "style": "Classic Traditional",
            "estimated_price": earring_price,
            "search_terms": "temple jewelry gold jhumka earrings"
        })
        recs.append({
            "item_type": "Bangles / Kada",
            "description": "Pair of openable zircon stone studded royal brass kadas",
            "style": "Festive Glam",
            "estimated_price": bangle_price,
            "search_terms": "antique gold plated openable bangles kada"
        })
    else:
        # Western / Contemporary / Minimalist
        watch_price = round(total * 0.40, 2)
        pendant_price = round(total * 0.35, 2)
        ring_price = round(total * 0.20, 2)

        recs.append({
            "item_type": "Pendant Necklace",
            "description": "Minimalist 925 Sterling Silver solitare pendant on delicate cable chain",
            "style": "Modern Minimalist",
            "estimated_price": pendant_price,
            "search_terms": "925 sterling silver solitaire pendant necklace"
        })
        recs.append({
            "item_type": "Bracelet / Watch",
            "description": "Rose gold mesh magnetic bracelet watch with mother-of-pearl dial",
            "style": "Sleek Contemporary",
            "estimated_price": watch_price,
            "search_terms": "rose gold sleek mesh watch bracelet women"
        })
        recs.append({
            "item_type": "Stackable Ring",
            "description": "Band ring set with cubic zirconia stones and anti-tarnish coating",
            "style": "Geometric Chic",
            "estimated_price": ring_price,
            "search_terms": "anti tarnish stackable cz band ring"
        })

    outfit_analysis = None
    if has_image:
        outfit_analysis = {
            "colors": ["Sapphire Blue", "Silver Frost Accents"],
            "style": "Contemporary Indo-Western" if is_traditional else "Modern Chic",
            "formality": "Festive Celebration" if is_traditional else "Smart Casual / Cocktail"
        }

    return {
        "outfit_analysis": outfit_analysis,
        "total_budget": total,
        "jewelry_recommendations": recs,
        "styling_tips": [
            "Keep the jewelry minimal if your outfit already features intricate embroidery or heavy neckwork.",
            "Coordinate metal finishes—match your watch hardware with your rings and earrings for a cohesive look.",
            "Consider hypoallergenic sterling silver or skin-friendly brass to avoid irritation during long events.",
            "CaratLane and Bluestone offer 15-day exchange and certified hallmarks for peace of mind."
        ]
    }
