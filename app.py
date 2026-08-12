import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
import json
from datetime import date, timedelta, datetime
import folium
from streamlit_folium import st_folium
from streamlit_js_eval import streamlit_js_eval
from nasa_power import fetch_nasa_power
from preprocess import compute_idi
from geopy.geocoders import Nominatim
from language import LANG, CROP_LABELS, SOURCE_LABELS
from PIL import Image
#  CONFIG
st.set_page_config(page_title="Farmer Advisory", layout="wide", page_icon="🌱")
PROFILE_PATH = "farmer_profile.json"

def profile_exists():
    return os.path.exists(PROFILE_PATH)

import os
import base64

def get_local_img(filename):
    p = os.path.join(BASE_DIR, "images", filename)
    return p if os.path.exists(p) else None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USERS_FILE = os.path.join(BASE_DIR, "users.json")
IMAGE_DIR  = os.path.join(BASE_DIR, "images")
LAST_LOGIN_FILE = os.path.join(BASE_DIR, "last_login.json")

#  GLOBAL CSS
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background-color:#ffffff; }

div[data-testid="stVerticalBlock"] {
    gap: 0.5rem !important;
}
div[data-testid="stVerticalBlock"] > div {
    background:transparent !important; border:none !important; box-shadow:none !important;
}
html,body,p,span,label,div,li { color:black !important; }
h1,h2,h3,h4                   { color:black !important; }
div[data-baseweb="select"]>div { background-color:#f2f2f2 !important; color:black !important; border-radius:6px; }
div[data-baseweb="select"] svg { fill:black !important; }
ul[role="listbox"]             { background-color:#f2f2f2 !important; }
li[role="option"]              { background-color:#f2f2f2 !important; color:black !important; }
li[role="option"]:hover        { background-color:#d9d9d9 !important; }
input                          { background-color:#f2f2f2 !important; color:black !important; }
.stButton>button               { background-color:#eeeeee; color:black; border-radius:8px; font-size:15px; }
.stButton>button:hover         { background-color:#cccccc; }
.stCheckbox div[role="checkbox"]                      { background-color:#f2f2f2 !important; border:1px solid #888 !important; }
.stCheckbox div[role="checkbox"][aria-checked="true"] { background-color:#4CAF50 !important; }
.stCheckbox label,.stRadio label                      { color:black !important; }
[data-testid="stMetricValue"]  { color:black !important; }
.stProgress>div>div            { background-color:#2E7D32; }

/* ── Top navbar ── */
.top-nav {
    display:flex; align-items:center; justify-content:space-between;
    padding:10px 0 16px 0; border-bottom:1.5px solid #e0e0e0; margin-bottom:18px;
}
.top-nav .app-title { font-size:24px; font-weight:800; color:#1b5e20 !important; }

/* ── Profile avatar button (top-right circle) ── */
.avatar-circle {
    width:40px; height:40px; border-radius:50%;
    background:linear-gradient(135deg,#43a047,#1b5e20);
    display:inline-flex; align-items:center; justify-content:center;
    font-size:19px; font-weight:700; color:white !important;
    cursor:pointer; border:2px solid #81c784;
    user-select:none; vertical-align:middle;
}

/* ── Google-style dark profile dropdown ── */
.gprofile-card {
    background:#2d2d2d;
    border-radius:18px;
    padding:24px 20px 16px 20px;
    width:300px;
    box-shadow:0 8px 32px rgba(0,0,0,0.38);
    text-align:center;
    margin-top:4px;
}
.gprofile-avatar-big {
    width:76px; height:76px; border-radius:50%;
    background:linear-gradient(135deg,#43a047,#1b5e20);
    display:inline-flex; align-items:center; justify-content:center;
    font-size:36px; font-weight:800; color:white !important;
    margin-bottom:10px;
}
.gprofile-hi {
    font-size:22px; font-weight:700;
    color:white !important; margin-bottom:2px;
}
.gprofile-phone {
    font-size:13px; color:#aaaaaa !important; margin-bottom:14px;
}
.gprofile-manage-btn {
    display:inline-block;
    border:1px solid #555; border-radius:20px;
    padding:7px 22px; font-size:14px;
    color:#e0e0e0 !important; background:transparent;
    margin-bottom:14px; cursor:pointer;
}
.gprofile-divider {
    border:none; border-top:1px solid #444; margin:0 0 12px 0;
}
.gprofile-actions {
    display:flex; justify-content:space-between; gap:8px;
}
.gprofile-action-btn {
    flex:1; background:#3a3a3a; border:none; border-radius:8px;
    padding:10px 6px; font-size:14px; color:#e0e0e0 !important;
    cursor:pointer; text-align:center;
}

/* ── Farm selector tabs ── */
.farm-tab {
    display:inline-block; padding:8px 18px; border-radius:20px;
    border:2px solid #81c784; margin:4px; cursor:pointer;
    font-size:14px; font-weight:600; background:white;
}
.farm-tab.active { background:#e8f5e9; border-color:#2e7d32; color:#1b5e20 !important; }

/* ── Zomato-style green banner ── */
.loc-banner {
    display:flex; align-items:center; gap:14px;
    background:#f0faf0; border:1.5px solid #81c784;
    border-radius:12px; padding:14px 20px; margin-bottom:12px;
}
.loc-banner .loc-hello { font-size:18px; font-weight:800; color:#1b5e20 !important; }
.loc-banner .loc-sub   { font-size:13px; color:#444 !important; margin-top:2px; }

/* ── Plant health scale ── */
.plant-scale { display:flex; justify-content:center; gap:0; margin:10px 0; padding:10px 0; }
.plant-stage { flex:1; text-align:center; padding:8px 4px; border-radius:10px;
               font-size:12px; font-weight:600; color:#555 !important; }
.plant-stage.active { background:#e8f5e9; border:2px solid #4CAF50; color:#1b5e20 !important; }

/* ── Countdown box ── */
.countdown-box {
    background:#fff8e1; border:2px solid #ffd54f;
    border-radius:14px; padding:20px; text-align:center;
}
.countdown-big  { font-size:52px; font-weight:900; line-height:1; }
.countdown-unit { font-size:16px; color:#555 !important; margin-top:4px; }
.countdown-msg  { font-size:15px; margin-top:10px; font-weight:600; }

/* ── Best time box ── */
.time-box {
    background:#e3f2fd; border:2px solid #90caf9;
    border-radius:14px; padding:18px; text-align:center;
}
.time-val { font-size:22px; font-weight:800; color:#0d47a1 !important; }
.time-sub { font-size:14px; color:#555 !important; }

/* ── Farm card ── */
.farm-card {
    background:#f9f9f9; border:1.5px solid #c8e6c9;
    border-radius:12px; padding:14px 18px; margin-bottom:8px;
}
.farm-card.selected { background:#e8f5e9; border-color:#2e7d32; }

/* ── Risk gauge card ── */
.risk-card {
    border-radius:16px; padding:22px 20px; text-align:center;
    margin-bottom:4px;
}
.risk-big   { font-size:58px; font-weight:900; line-height:1; }
.risk-label { font-size:16px; font-weight:700; margin-top:6px; }
.risk-sub   { font-size:13px; color:#666 !important; margin-top:4px; }

/* ── Rain probability bar ── */
.rain-bar-wrap {
    background:#e3f2fd; border:1.5px solid #90caf9;
    border-radius:14px; padding:18px 20px;
}
.rain-bar-label { font-size:15px; font-weight:700; color:#0d47a1 !important; margin-bottom:6px; }
.rain-outer {
    background:#bbdefb; border-radius:20px; height:28px;
    width:100%; overflow:hidden; position:relative;
}
.rain-inner {
    height:100%; border-radius:20px;
    display:flex; align-items:center; justify-content:flex-end;
    padding-right:10px;
    font-size:13px; font-weight:700; color:white !important;
    transition: width 0.4s;
}
.rain-row { display:flex; align-items:center; gap:10px; margin-bottom:10px; }
.rain-day  { font-size:13px; font-weight:600; color:#333 !important; width:60px; flex-shrink:0; }
.rain-icon { font-size:18px; flex-shrink:0; }
</style>
""", unsafe_allow_html=True)


from streamlit_js_eval import streamlit_js_eval

CROPS = ["Rice", "Cotton", "Groundnut", "Ragi", "Sugarcane"]
CROP_IMG = {
    "Rice": "rice.jpg", 
    "Cotton": "cotton.jpg",
    "Groundnut": "Groundnut.jpg", 
    "Ragi": "ragi.jpg",
    "Sugarcane": "Sugar cane.jpg",
}
CROP_FACTOR = {
    "Rice": 1.2, "Sugarcane": 1.3, "Cotton": 1.0,
    "Groundnut": 0.8, "Ragi": 0.6,
}
CROP_SURVIVAL_HOURS = {
    "Rice": 20, "Sugarcane": 48, "Cotton": 72, "Groundnut": 72, "Ragi": 96,
}

SOURCES = ["Rain", "Borewell", "Motor", "Canal", "Drip"]
SOURCE_IMG = {
    "Rain": "rainfall.jpg", 
    "Borewell": "borewell.jpg",
    "Motor": "motor pumps.jpg", 
    "Canal": "cannal irrigation.jpg",
    "Drip": "drip irrigation.jpg",
}
SOURCE_FACTOR = {
    "rain": 1.3, "borewell": 0.9, "motor": 0.85, "canal": 0.8, "drip": 0.7,
}

PLANT_STAGES = [
    {"label": "Fully Healthy",   "emoji": "🌳", "color": "#2e7d32", "msg": "Your crop is in excellent condition.",      "img": "images/images/healthy.jpg"},
    {"label": "Slight Stress",   "emoji": "🌿", "color": "#558b2f", "msg": "Minor stress. Keep an eye on your field.",  "img": "images/images/phase2.jpg"},
    {"label": "Moderate Stress", "emoji": "🍃", "color": "#f9a825", "msg": "Irrigation recommended soon.",              "img": "images/images/moderate.jpg"},
    {"label": "High Stress",     "emoji": "🍂", "color": "#e65100", "msg": "Irrigate your crop soon!",                  "img": "images/images/phase4.jpg"},
    {"label": "Severe / Wilted", "emoji": "🥀", "color": "#b71c1c", "msg": "Immediate irrigation required urgently!",   "img": "images/images/severe.jpg"},
]

PLANT_EMOJI = ["🌳", "🌿", "🍃", "🍂", "🥀"]

def T(key):
    lang = st.session_state.get("lang", "English")
    return LANG[lang].get(key, key)

def stage_key(label):
    mapping = {
        "Fully Healthy": "fully_healthy",
        "Slight Stress": "slight_stress",
        "Moderate Stress": "moderate_stress",
        "High Stress": "high_stress",
        "Severe / Wilted": "severe_wilted"
    }
    return mapping.get(label, label)
def stage_msg_key(label):
    mapping = {
        "Fully Healthy": "msg_fully_healthy",
        "Slight Stress": "msg_slight_stress",
        "Moderate Stress": "msg_moderate_stress",
        "High Stress": "msg_high_stress",
        "Severe / Wilted": "msg_severe_wilted"
    }
    return mapping.get(label, label)

#  HELPERS
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    return {}

def save_users(u):
    with open(USERS_FILE, "w") as f:
        json.dump(u, f, indent=2)

def get_user(phone):    return load_users().get(phone)
def upsert_user(ph, d): u = load_users(); u[ph] = d; save_users(u)

def is_duplicate_farm(new_farm: dict, existing_farms: list, skip_index: int = -1) -> bool:
    """
    Returns True if new_farm is a duplicate of any existing farm.
    Duplicate = same name OR very close coordinates (Geofencing).
    """
    name_new = new_farm.get("farm_name", "").strip().lower()
    lat_new  = new_farm.get("lat")
    lon_new  = new_farm.get("lon")

    for i, f in enumerate(existing_farms):
        if i == skip_index:
            continue
            
        name_ex = f.get("farm_name", "").strip().lower()
        lat_ex  = f.get("lat")
        lon_ex  = f.get("lon")

        # 1. Check for Duplicate Name
        if name_new and name_new == name_ex:
            return True

        # 2. Check for Duplicate Location (Geofencing)
        if all(v is not None for v in [lat_new, lon_new, lat_ex, lon_ex]):
            # Change 0.01 to 0.0005 (approx 50 meters)
            # This allows neighbors to have different accounts but blocks 
            # clicking the 'Locate' button twice for the same spot.
            if abs(lat_new - lat_ex) < 0.0005 and abs(lon_new - lon_ex) < 0.0005:
                return True
                
    return False

def compute_risk_percent(idi: float) -> float:
    """Convert IDI to 0-100 risk % for display."""
    if idi <= 0:   return 0.0
    if idi >= 40:  return 100.0
    return round((idi / 40) * 100, 1)

def get_risk_display(risk: float) -> dict:
    if risk < 25:
        return {
            "label": T("low_risk"),
            "color": "#2e7d32",
            "bg": "#e8f5e9",
            "emoji": "✅",
            "msg": T("risk_safe")
        }

    elif risk < 50:
        return {
            "label": T("moderate_risk"),
            "color": "#f57f17",
            "bg": "#fff8e1",
            "emoji": "⚠️",
            "msg": T("risk_watch")
        }

    elif risk < 75:
        return {
            "label": T("high_risk"),
            "color": "#e65100",
            "bg": "#fff3e0",
            "emoji": "🔶",
            "msg": T("risk_plan")
        }

    else:
        return {
            "label": T("very_high_risk"),
            "color": "#b71c1c",
            "bg": "#ffebee",
            "emoji": "🚨",
            "msg": T("risk_now")
        }
    
def get_rain_forecast(df: "pd.DataFrame") -> list:
    """
    Derive a simple 7-day rain probability from NASA rainfall data.
    Uses actual rainfall values — converts to a 0-100% chance per day.
    Returns list of dicts: {day, date_str, prob, mm, icon}
    """
    result = []
    today  = date.today()
    rows   = df.tail(7).reset_index(drop=True)
    # Historical max rainfall in dataset as reference cap
    max_rain = max(df["rainfall"].max(), 10.0)
    DAY_NAMES = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    for i, row in rows.iterrows():
        mm   = float(row["rainfall"]) if row["rainfall"] > 0 else 0.0
        prob = min(100, round((mm / max_rain) * 100))
        d    = row["date"] if hasattr(row["date"], "strftime") else today - timedelta(days=6-i)
        day_name = d.strftime("%a") if hasattr(d, "strftime") else DAY_NAMES[i % 7]
        date_str = d.strftime("%d %b") if hasattr(d, "strftime") else ""

        if prob == 0:     icon = "☀️"
        elif prob < 20:   icon = "🌤️"
        elif prob < 50:   icon = "⛅"
        elif prob < 75:   icon = "🌧️"
        else:             icon = "🌧️"

        result.append({"day": day_name, "date_str": date_str,
                        "prob": prob, "mm": round(mm, 1), "icon": icon})
    return result

def get_local_img(filename):
    p = os.path.join(BASE_DIR, "images", filename)
    return p if os.path.exists(p) else None

def get_plant_stage_index(idi):
    if idi < 5:    return 0
    elif idi < 15: return 1
    elif idi < 25: return 2
    elif idi < 35: return 3
    else:          return 4

def get_best_irrigation_time(eto):
    if eto > 6:
        return {
            "time": T("early_morning_evening"),
            "reason": T("very_hot_reason"),
            "avoid": T("avoid_midday")
        }

    elif eto > 4:
        return {
            "time": T("morning_time"),
            "reason": T("moderate_heat_reason"),
            "avoid": T("avoid_afternoon")
        }

    else:
        return {
            "time": T("anytime_morning"),
            "reason": T("mild_weather_reason"),
            "avoid": ""
        }

def get_irrigation_duration(crop, water_sources, risk_pct, irrigated, farm_area):
    base = {
        "Rice": 60,
        "Cotton": 40,
        "Groundnut": 30,
        "Ragi": 25,
        "Sugarcane": 75
    }.get(crop, 40)

    if "drip" in water_sources:
        base *= 0.7
    elif "canal" in water_sources:
        base *= 1.2
    elif "borewell" in water_sources:
        base *= 1.0
    elif "motor" in water_sources:
        base *= 1.1

    factor = risk_pct / 100
    if irrigated:
        factor *= 0.5
    base *= farm_area
    minutes = int(base * factor)

    return max(minutes, 5)

def get_safe_delay(idi, crop, irrigated):
    """Returns hours remaining and a farmer-friendly message."""
    base_hours = CROP_SURVIVAL_HOURS.get(crop, 48)
    if irrigated:
        base_hours += 12

    if idi < 5:    hours = base_hours + 48
    elif idi < 15: hours = base_hours
    elif idi < 25: hours = max(12, base_hours // 2)
    elif idi < 35: hours = 12
    else:          hours = 0

    if hours == 0:
        return {
            "hours": 0,
            "display": "0",
            "unit": T("hours"),
            "msg": f"🚨 {T('irrigate_now')}",
            "color": "#b71c1c"
        }

    elif hours < 24:
        return {
            "hours": hours,
            "display": str(hours),
            "unit": T("hours_left"),
            "msg": f"⚠️ {T('irrigate_within')} {hours} {T('hours')}",
            "color": "#e65100"
        }

    else:
        days = hours // 24
        rem = hours % 24

        if rem == 0:
            disp = str(days)
            unit = T("days_safe")

        else:
            disp = f"{days}d {rem}h"
            unit = T("safe_to_wait")

        color = "#2e7d32" if days >= 2 else "#f57f17"

        return {
            "hours": hours,
            "display": disp,
            "unit": unit,
            "msg": f"✅ {T('safe_about')} {days} {T('days')}",
            "color": color
        }

LAST_LOGIN_FILE = os.path.join(BASE_DIR, "last_login.json")
def save_last_login(phone):
    with open(LAST_LOGIN_FILE, "w") as f:
        json.dump({"phone": phone}, f)

def load_last_login():
    if os.path.exists(LAST_LOGIN_FILE):
        with open(LAST_LOGIN_FILE) as f:
            return json.load(f).get("phone")
    return None

def clear_last_login():
    if os.path.exists(LAST_LOGIN_FILE):
        os.remove(LAST_LOGIN_FILE)

#  SESSION STATE DEFAULTS
DEFAULTS = {
    "page":         "login",   # login | signup | main | edit_profile
    "phone":        None,
    "profile":      None,
    "active_farm":  0,         # index of currently selected farm
    "show_profile": False,     # profile dropdown open?
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

#  SHARED: top navbar with profile avatar
def render_navbar(show_profile_btn=True):
    """Renders top nav bar. Profile button only shown when logged in."""
    profile = st.session_state.profile
    left, mid, right = st.columns([6,2,2])

    with mid:
        if "lang" not in st.session_state:
            st.session_state.lang = "English"
        st.markdown("🌐 Language")
        selected_lang = st.selectbox(
            "", ["English", "Telugu", "Kannada", "Tamil", "Hindi", "Malayalam"],
            index=["English", "Telugu", "Kannada", "Tamil", "Hindi", "Malayalam"].index(st.session_state.lang),
            key="lang_selector"
        )

        if selected_lang != st.session_state.lang:
            st.session_state.lang = selected_lang
            st.experimental_rerun()

    with left:
        st.markdown(
            f"<div style='font-size:26px;font-weight:900;color:#1b5e20;padding-top:6px'>"
            f"🌱 {T('farmer_advisory_system')}</div>",
            unsafe_allow_html=True
        )

    if show_profile_btn and profile:
        with right:
            name    = profile.get("name", "?")
            initial = name[0].upper()

            # Avatar + name shown as button area
            col_a, col_b = st.columns([1, 2])
            with col_a:
                st.markdown(
                    f"<div class='avatar-circle'>{initial}</div>",
                    unsafe_allow_html=True
                )
            with col_b:
                if st.button("▼ " + name.split()[0], key="profile_toggle"):
                    st.session_state.show_profile = not st.session_state.show_profile
                    st.experimental_rerun()

        # Dropdown panel — Google style dark card
        if st.session_state.show_profile:
            _, drop_col, _ = st.columns([5, 2, 1])
            with drop_col:
                st.markdown(f"""
                <div class="gprofile-card">
                    <div class="gprofile-avatar-big">{initial}</div>
                    <div class="gprofile-hi">Hi, {profile['name'].split()[0]}!</div>
                    <div class="gprofile-phone">📱 {st.session_state.phone}</div>
                    <hr class="gprofile-divider"/>
                </div>
                """, unsafe_allow_html=True)

                ep_col, lo_col = st.columns(2)
                with ep_col:
                    if st.button(f"✏️  {T('edit_profile')}", key="goto_edit", use_container_width=True):
                        st.session_state.show_profile = False
                        st.session_state.page = "edit_profile"
                        st.experimental_rerun()
                with lo_col:
                    if st.button(f"↪  {T('sign_out')}", key="nav_logout", use_container_width=True):
                        clear_last_login()
                        for k in DEFAULTS:
                            st.session_state[k] = DEFAULTS[k]
                        st.session_state.phone = None
                        st.session_state.profile = None
                        st.session_state.page = "login"
                        st.experimental_rerun()

    st.markdown("<hr style='margin:8px 0 18px 0;border-color:#e0e0e0'>", unsafe_allow_html=True)

#  REFACTORED: Single Farm Form (GPS Automated)
from geopy.geocoders import Nominatim

def farm_form(prefix, existing=None):

    ex = existing or {}

    farm_name = st.text_input(
        T("farm_name"),
        value=ex.get("farm_name", ""),
        key=f"{prefix}_farm_name"
    )
    farm_area = st.number_input(
        T("farm_area"),
        min_value=0.1,
        max_value=100.0,
        value=float(ex.get("farm_area", 1.0)),
        step=0.1,
        key=f"{prefix}_farm_area"
    )
    if f"{prefix}_lat" not in st.session_state:
        st.session_state[f"{prefix}_lat"] = ex.get("lat", 17.3850)

    if f"{prefix}_lon" not in st.session_state:
        st.session_state[f"{prefix}_lon"] = ex.get("lon", 78.4867)

    st.markdown(f"## 📍 {T('set_location')}")

    place = st.text_input(
        T("enter_place"),
        placeholder=T("place_placeholder"),
        key=f"{prefix}_place"
    )

    if st.button(T("search_location"), key=f"{prefix}_search_btn"):

        geolocator = Nominatim(user_agent="farm_locator")

        location = geolocator.geocode(place)

        if location:

            st.session_state[f"{prefix}_lat"] = location.latitude
            st.session_state[f"{prefix}_lon"] = location.longitude

            st.success(f"✅ {T('location_found')}")

        else:
            st.warning(f"⚠️ {T('try_location_more')}")

    lat = st.session_state[f"{prefix}_lat"]
    lon = st.session_state[f"{prefix}_lon"]

    st.success(f"📍 {T('final_location')}: {lat:.6f}, {lon:.6f}")

    # -----------------------
    # GOOGLE MAP LINK
    # -----------------------
    map_url = f"https://www.google.com/maps?q={lat},{lon}"

    st.markdown(
        f"[🌍 {T('open_google_maps')}]({map_url})"
    )

    st.info(f"⚠️ {T('verify_map')}")
    st.markdown(f"### 📌 {T('paste_coordinates')}")

    st.info(T("copy_coordinates_help"))

    coord_input = st.text_input(
        T("paste_coordinates"),
        placeholder=T("coord_placeholder"),
        key=f"{prefix}_coord_input"
    )

    if st.button(T("set_coordinates"), key=f"{prefix}_coord_btn"):

        try:
            lat, lon = coord_input.split(",")

            st.session_state[f"{prefix}_lat"] = float(round(float(lat.strip()), 6))
            st.session_state[f"{prefix}_lon"] = float(round(float(lon.strip()), 6))

            st.success(f"✅ {T('coordinates_set')}")

        except:
            st.error(f"❌ {T('coord_format')}")

    # CROP
    crop_key = f"{prefix}_crop"

    if crop_key not in st.session_state:
        st.session_state[crop_key] = ex.get("crop")

    st.markdown(f"## 🌾 {T('select_crop')}")
    cols = st.columns(3)

    for i, crop in enumerate(CROPS):
        with cols[i % 3]:

            img_path = os.path.join(BASE_DIR, "images", CROP_IMG[crop])

            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, width=120)
            crop_label = CROP_LABELS[st.session_state.lang][crop]

            if st.button(crop_label, key=f"{prefix}_{crop}"):
                st.session_state[crop_key] = crop

    # WATER SOURCES
    st.markdown(f"## 💧 {T('water_sources')}")

    selected_sources = []

    cols = st.columns(3)

    for i, src in enumerate(SOURCES):
        with cols[i % 3]:

            img_path = os.path.join(BASE_DIR, "images", SOURCE_IMG[src])

            if os.path.exists(img_path):
                img = Image.open(img_path)
                st.image(img, width=110)

            if st.checkbox(
                SOURCE_LABELS[st.session_state.lang][src],
                value=src.lower() in ex.get("water_sources", []),
                key=f"{prefix}_{src}"
            ):
                selected_sources.append(src.lower())
    
    return {
        "farm_name": farm_name,
        "farm_area": farm_area,
        "lat": st.session_state[f"{prefix}_lat"],
        "lon": st.session_state[f"{prefix}_lon"],
        "region_label": f"{float(st.session_state[f'{prefix}_lat']):.4f}, {float(st.session_state[f'{prefix}_lon']):.4f}",
        "crop": st.session_state.get(crop_key),
        "water_sources": selected_sources,
    }

#  PAGE — LOGIN
def page_login():
    render_navbar(show_profile_btn=False)

    _, mid, _ = st.columns([1, 2, 1])
    with mid:
        st.markdown(f"#### 👋 {T('welcome_login')}")
        st.markdown("")

        phone = st.text_input(
                    f"📱 {T('mobile_number')}",
                    placeholder=T('mobile_placeholder')
                )
        c1, c2 = st.columns(2)
        with c1:
            if st.button(f"➡️ {T('login')}", use_container_width=True):
                if len(phone) != 10 or not phone.isdigit():
                    st.error(T("valid_mobile"))
                else:
                    user = get_user(phone)
                    if user:
                        farms_count = len(user.get("farms", []))
                        st.session_state.phone       = phone
                        save_last_login(phone)
                        st.session_state.profile     = user
                        st.session_state.active_farm = 0 if farms_count > 0 else 0
                        st.session_state.page        = "main"
                        st.experimental_rerun()
                    else:
                        st.warning(T("no_account"))
        with c2:
            if st.button(f"📝 {T('create_account')}", use_container_width=True):
                if len(phone) == 10 and phone.isdigit():
                    if get_user(phone):
                        st.info(T("account_exists"))
                    else:
                        st.session_state.phone = phone
                        st.session_state.page  = "signup"
                        st.experimental_rerun()
                else:
                    st.error(T("valid_mobile"))

#  PAGE — SIGNUP  (name + multiple farms)
def page_signup():
    render_navbar(show_profile_btn=False)

    st.title(f"📝 {T('create_account_title')}")
    st.info(f"📱 {T('new_account_for')} **{st.session_state.phone}**")
    st.caption(T("signup_caption"))
    st.markdown("---")

    # ── Name ──
    name = st.text_input(
        f"👤 {T('your_name')}",
        placeholder=T("name_placeholder")
    )

    # ── How many farms ──
    st.markdown("---")
    st.subheader(f"🌾 {T('your_farms')}")
    st.caption(T("farm_caption"))

    n_farms = st.number_input(T("how_many_farms"),
                               min_value=1, max_value=5, value=1, step=1)

    farms_data = []
    for i in range(int(n_farms)):
        st.markdown(f"---")
        st.markdown(f"#### 🏡 Farm {i+1}")
        fd = farm_form(prefix=f"farm{i}")
        farms_data.append(fd)

    # ── Save ──
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"💾 {T('save_start')}", use_container_width=True):
            errors = []
            if not name.strip():
                errors.append("❌ Enter your name.")
            for i, fd in enumerate(farms_data):
                if not fd["farm_name"].strip():
                    errors.append(f"❌ Farm {i+1}: Enter a farm name.")
                if fd["farm_area"] <= 0:
                    errors.append(f"❌ Farm {i+1}: Enter farm area.")
                if fd["lat"] is None:
                    errors.append(f"❌ Farm {i+1}: Set location.")
                if not fd["crop"]:
                    errors.append(f"❌ Farm {i+1}: Select a crop.")
                if not fd["water_sources"]:
                    errors.append(f"❌ Farm {i+1}: Select water sources.")

            # Duplicate detection
            if not errors:
                seen = []
                for i, fd in enumerate(farms_data):
                    if is_duplicate_farm(fd, seen):
                        errors.append(
                            f"❌ Farm {i+1} \"{fd['farm_name']}\" is a duplicate — "
                            f"same name or same location as another farm you added."
                        )
                    else:
                        seen.append(fd)

            if errors:
                for e in errors: st.error(e)
            else:
                profile = {"name": name.strip(), "farms": farms_data}
                upsert_user(st.session_state.phone, profile)
                st.session_state.profile     = profile
                st.session_state.active_farm = 0
                st.session_state.page        = "main"
                st.experimental_rerun()
    with c2:
        if st.button(f"← {T('back_login')}", use_container_width=True):
            st.session_state.page = "login"; st.experimental_rerun()

#  PAGE — MAIN APP
def page_main():
    profile = st.session_state.profile
    phone   = st.session_state.phone
    farms   = profile.get("farms", [])
    render_navbar(show_profile_btn=True)

    # ── Farm selector (like tabs) ──
    if len(farms) > 1:
        st.markdown(f"### 🏡 {T('choose_farm')}")
        farm_labels = [f.get("farm_name", f"Farm {i+1}") for i, f in enumerate(farms)]

        cols = st.columns(len(farms))
        for i, lbl in enumerate(farm_labels):
            with cols[i]:
                is_active = st.session_state.active_farm == i
                btn_label = f"✅ {lbl}" if is_active else f"🏡 {lbl}"
                if st.button(btn_label, key=f"farm_sel_{i}", use_container_width=True):
                    st.session_state.active_farm = i
                    st.experimental_rerun()
        st.markdown("")

    # ── Active farm ── (guard against empty or stale index)
    if not farms:
        st.warning("No farms found. Please edit your profile and add a farm.")
        if st.button("➕ Go to Edit Profile"):
            st.session_state.page = "edit_profile"
            st.experimental_rerun()
        st.stop()

    farm_idx = st.session_state.active_farm
    if not isinstance(farm_idx, int) or farm_idx < 0 or farm_idx >= len(farms):
        farm_idx = 0
        st.session_state.active_farm = 0

    farm = farms[farm_idx]
    farm_area = farm.get("farm_area", 1.0)
    crop = farm.get("crop")
    water_sources = farm.get("water_sources", [])
    # ── Green banner ──
    crop = farm.get("crop", "—")
    st.markdown(f"""
    <div class="loc-banner">
        <span style="font-size:34px">📍</span>
        <div>
            <div class="loc-hello">
                👋 {T('hello')}, {profile['name']}! &nbsp;|&nbsp;
                🏡 {farm.get('farm_name','Farm')}
            </div>
            <div class="loc-sub">
                {T('location')}: <b>{farm.get('region_label','—')}</b>
                &nbsp;|&nbsp; 🌾 {T('crop_label')}: <b>{CROP_LABELS[st.session_state.lang].get(crop, crop)}</b>
                &nbsp;|&nbsp; 📏 {farm_area} acres
                &nbsp;|&nbsp; 📱 {phone}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    lat = farm.get("lat"); lon = farm.get("lon")
    st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=8)

    # ── Recently Irrigated ──
    st.markdown("---")
    st.subheader(f"💦 {T('did_irrigate')}")
    irrigated_str = st.radio("", [T('no'), T('yes')], horizontal=True)
    irrigated     = irrigated_str == T('yes')

    # ── RUN ──
    st.markdown("---")
    run = st.button(f"🔍 {T('check_farm')}", use_container_width=True)

    if run:
        saved_sources = farm.get("water_sources", [])
        if not crop or crop == "—":
            st.warning("No crop set for this farm. Please edit your profile."); st.stop()
        if not saved_sources:
            st.warning("No water sources set. Please edit your profile."); st.stop()

        with st.spinner("🌐 Fetching NASA weather data..."):
            today      = date.today()
            start_date = today - timedelta(days=7)
            end_date   = today
            try:
                df = fetch_nasa_power(lat, lon,
                                      start_date.strftime("%Y%m%d"),
                                      end_date.strftime("%Y%m%d"))
            except Exception as e:
                st.error(f"NASA API error: {e}"); st.stop()

        df = compute_idi(df)
        latest = df.iloc[-1]

        features = pd.DataFrame([{
            "rainfall": latest["rainfall"],
            "eto": latest["eto"],
        }])

        prediction = model.predict(features)[0]
        if df.empty:
            st.warning("No weather data available."); st.stop()

        idi = latest["idi_7day"]
        idi *= CROP_FACTOR.get(crop, 1.0)
        factor = 1.0
        for s in saved_sources:
            factor *= SOURCE_FACTOR.get(s, 1.0)
        idi *= factor
        if irrigated: idi *= 0.7

        avg_eto    = df["eto"].mean()
        stage_idx  = get_plant_stage_index(idi)
        stage      = PLANT_STAGES[stage_idx]
        best_time  = get_best_irrigation_time(avg_eto)
        safe_delay = get_safe_delay(idi, crop, irrigated)
        # ML-based risk using trained model prediction
        if prediction == 1:
            risk_pct = 85
        else:
            risk_pct = 20
        risk_info  = get_risk_display(risk_pct)
        water_sources = farm.get("water_sources", [])
        duration = get_irrigation_duration(crop, water_sources, risk_pct, irrigated, farm_area)
        rain_days  = get_rain_forecast(df)

        st.markdown("---")
        st.markdown(f"## 📊 {T('farm_report')}")

        # ══ 1. CROP HEALTH ══════════════════════
        st.markdown(f"### 🌿 {T('crop_health')}")

        local_img = get_local_img(stage["img"])
        card_col, info_col = st.columns([1, 2])
        with card_col:
            if local_img:
                st.image(local_img, width=200)
            else:
                st.markdown(
                    f"<div style='font-size:110px;text-align:center;padding:10px'>"
                    f"{stage['emoji']}</div>",
                    unsafe_allow_html=True
                )
        with info_col:
            st.markdown(
                f"<div style='font-size:28px;font-weight:800;color:{stage['color']}'>"
                f"{stage['emoji']} {T(stage_key(stage['label']))}</div>",
                unsafe_allow_html=True
            )
            st.markdown(
                f"<div style='font-size:18px;margin-top:10px;color:#333'>{T(stage_msg_key(stage['label']))}</div>",
                unsafe_allow_html=True
            )
            if stage_idx == 0:
                st.success(f"✅ {T('no_irrigation_now')}")
            elif stage_idx in [1, 2]:
                st.warning(f"⚠️ {T('irrigation_soon')}")
            else:
                st.error(f"🚨 {T('irrigation_now')}")

        # Health scale
        st.markdown(f"#### 🌡️ {T('crop_health_scale')}")
        arrows = ["&nbsp;" * 6] * 5
        arrows[stage_idx] = "⬇️"
        arrow_html = "<div style='display:flex;'>" + "".join(
            f"<div style='flex:1;text-align:center;font-size:20px'>{a}</div>" for a in arrows
        ) + "</div>"
        st.markdown(arrow_html, unsafe_allow_html=True)

        scale_html = "<div class='plant-scale'>"
        for i, s in enumerate(PLANT_STAGES):
            ac = "active" if i == stage_idx else ""
            scale_html += (
                f"<div class='plant-stage {ac}'>"
                f"<div style='font-size:28px'>{PLANT_EMOJI[i]}</div>"
                f"<div>{T(s['label'].lower().replace(' / ', '_').replace(' ', '_'))}</div></div>"
            )
        scale_html += "</div>"
        st.markdown(scale_html, unsafe_allow_html=True)

        # If local phase images exist, show them in a row
        phase_imgs = [(get_local_img(s["img"]), s["label"], s["color"]) for s in PLANT_STAGES]
        if all(p[0] for p in phase_imgs):
            st.markdown("#### 📸 Plant Condition Gallery")
            img_cols = st.columns(5)
            for i, (p, lbl, col) in enumerate(phase_imgs):
                with img_cols[i]:
                    border = "3px solid #4CAF50" if i == stage_idx else "2px solid #eee"
                    st.markdown(
                        f"<div style='border:{border};border-radius:10px;padding:4px;text-align:center'>",
                        unsafe_allow_html=True
                    )
                    st.image(p, width=110)
                    st.markdown(
                        f"<div style='font-size:12px;font-weight:700;color:{col}'>{lbl}</div></div>",
                        unsafe_allow_html=True
                    )

        # ══ 2. SAFE DELAY COUNTDOWN ═════════════
        st.markdown("---")
        st.markdown(f"### ⏳ {T('safe_delay')}")
        st.caption(T('safe_delay_caption'))
        dcol1, dcol2 = st.columns([1, 2])
        with dcol1:
            st.markdown(f"""
            <div class="countdown-box">
                <div class="countdown-big" style="color:{safe_delay['color']} !important">
                    {safe_delay['display']}
                </div>
                <div class="countdown-unit">{safe_delay['unit']}</div>
                <div class="countdown-msg" style="color:{safe_delay['color']} !important">
                    {safe_delay['msg']}
                </div>
            </div>
            """, unsafe_allow_html=True)
        with dcol2:
            st.markdown(
                f"<div style='padding-top:16px'>"
                f"<div style='font-size:17px;color:#333'>"
                f"{T('crop')}: <b>{crop}</b> &nbsp;|&nbsp; "
                f"{T('recent_irrigated')}: <b>{T('yes')+' ✅' if irrigated else T('no')}</b>"
                f"{T('safe_delay_desc')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )

        # ══ 3. BEST IRRIGATION TIME ═════════════
        st.markdown("---")
        st.markdown(f"### 🕐 {T('best_irrigation_time')}")
        tcol1, tcol2 = st.columns([1, 2])
        with tcol1:
            st.markdown(f"""
            <div class="time-box">
                <div style="font-size:40px">🕐</div>
                <div class="time-val">{best_time['time']}</div>
            </div>
            """, unsafe_allow_html=True)
        with tcol2:
            st.markdown(
                f"<div style='padding-top:14px'>"
                f"<div style='font-size:17px;color:#333'><b>{T('why')}</b> {best_time['reason']}</div>",
                unsafe_allow_html=True
            )
            if best_time["avoid"]:
                st.markdown(
                    f"<div style='font-size:15px;color:#c62828;margin-top:8px'>{best_time['avoid']}</div>",
                    unsafe_allow_html=True
                )
            st.markdown("</div>", unsafe_allow_html=True)
        if "motor" in water_sources:
            st.success(f"💧 {T('run_motor')} {duration} {T('minutes')}")

        elif "drip" in water_sources:
            st.success(f"💧 {T('run_drip')} {duration} {T('minutes')}")

        else:
            st.success(f"💧 {T('irrigate_for')} {duration} {T('minutes')}")

        # ══ 4. RISK PERCENTAGE ══════════════════
        st.markdown("---")
        st.markdown(f"### 🎯 {T('irrigation_risk')}")

        r1, r2 = st.columns([1, 2])
        with r1:
            st.markdown(f"""
            <div class="risk-card" style="background:{risk_info['bg']};
                 border:2px solid {risk_info['color']};">
                <div class="risk-big" style="color:{risk_info['color']} !important">
                    {risk_pct:.0f}%
                </div>
                <div class="risk-label" style="color:{risk_info['color']} !important">
                    {risk_info['emoji']} {risk_info['label']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with r2:
            st.markdown(
                f"<div style='padding-top:10px'>"
                f"<div style='font-size:20px;font-weight:700;color:{risk_info['color']}'>"
                f"{risk_info['msg']}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
            # Visual progress bar (5 blocks)
            filled   = int(risk_pct // 20)   # 0–5 filled blocks
            bar_html = "<div style='display:flex;gap:6px;margin-top:14px'>"
            block_colors = ["#2e7d32","#558b2f","#f9a825","#e65100","#b71c1c"]
            block_labels = [
                T("very_low"),
                T("low"),
                T("moderate"),
                T("high"),
                T("very_high")
            ]
            for bi in range(5):
                bg = block_colors[bi] if bi < filled or (bi == filled and risk_pct % 20 > 0) else "#e0e0e0"
                bar_html += (
                    f"<div style='flex:1;background:{bg};height:22px;"
                    f"border-radius:6px'></div>"
                )
            bar_html += "</div>"
            bar_html += (
                f"<div style='display:flex;justify-content:space-between;"
                f"font-size:11px;color:#888;margin-top:4px'>"
                f"<span>0%</span><span>25%</span><span>50%</span>"
                f"<span>75%</span><span>100%</span></div>"
            )
            st.markdown(bar_html, unsafe_allow_html=True)

        # ══ 5. RAIN PROBABILITY (7-day) ══════════
        st.markdown("---")
        st.markdown(f"### 🌧️ {T('rain_forecast_7days')}")
        st.caption(T("rain_caption"))

        rain_html = "<div class='rain-bar-wrap'>"
        for rd in rain_days:
            prob  = rd["prob"]
            mm    = rd["mm"]
            # bar color: blue shades by intensity
            if prob == 0:    bar_color = "#90caf9"
            elif prob < 30:  bar_color = "#42a5f5"
            elif prob < 60:  bar_color = "#1565c0"
            else:            bar_color = "#0d47a1"
            width = max(4, prob)  # min 4% so bar is always visible

            # Farmer-friendly label instead of raw %
            if prob == 0:
                plain = T("no_rain")
            elif prob < 20:
                plain = T("very_little_rain")
            elif prob < 40:
                plain = T("light_rain")
            elif prob < 65:
                plain = T("moderate_rain")
            elif prob < 85:
                plain = T("good_rain")
            else:
                plain = T("heavy_rain")

            rain_html += f"""
            <div class="rain-row">
                <div class="rain-icon">{rd['icon']}</div>
                <div class="rain-day">{rd['day']}<br>
                    <span style="font-size:11px;color:#888">{rd['date_str']}</span>
                </div>
                <div style="flex:1">
                    <div class="rain-outer">
                        <div class="rain-inner"
                             style="width:{width}%;background:{bar_color}">
                            {prob}%
                        </div>
                    </div>
                    <div style="font-size:12px;color:#555;margin-top:2px">
                        {plain} &nbsp;({mm} mm)
                    </div>
                </div>
            </div>"""
        rain_html += "</div>"
        st.markdown(rain_html, unsafe_allow_html=True)

        # Rain advice based on forecast
        total_mm = sum(rd["mm"] for rd in rain_days)
        if total_mm > 20:
            st.success(f"🌧️ {T('rain_good')}")
        elif total_mm > 5:
            st.info(f"🌤️ {T('rain_some')}")
        else:
            st.warning(f"☀️ {T('rain_low')}")

        # ══ 6. WATER STRESS TREND ═══════════════
        st.markdown("---")
        st.markdown(f"### 📈 {T('water_stress_trend')}")

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["idi_7day"],
            mode="lines+markers",
            line=dict(color="#2E7D32", width=3),
            marker=dict(size=7, color="#2E7D32"),
        ))
        fig.update_layout(
            plot_bgcolor="white", paper_bgcolor="white",
            font=dict(color="black", size=13),
            xaxis=dict(title=T("date"),
                       title_font=dict(color="black", size=14),
                       tickfont=dict(color="black", size=12),
                       showgrid=True, gridcolor="#eeeeee",
                       linecolor="black", linewidth=1),
            yaxis=dict(title=T("water_stress_level"),
                       title_font=dict(color="black", size=14),
                       tickfont=dict(color="black", size=12),
                       showgrid=True, gridcolor="#eeeeee",
                       linecolor="black", linewidth=1),
            margin=dict(l=60, r=20, t=30, b=60),
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)


# ════════════════════════════════════════════════════════════════
#  PAGE — EDIT PROFILE
# ════════════════════════════════════════════════════════════════
def page_edit_profile():
    profile = st.session_state.profile
    phone   = st.session_state.phone
    farms   = profile.get("farms", [])

    render_navbar(show_profile_btn=True)

    st.title(f"⚙️ {T('edit_profile')}")
    st.caption(T("save_changes_caption"))

    # ── Name ──
    st.subheader(f"👤 {T('your_name')}")
    new_name = st.text_input(f" {T('name')}", value=profile.get("name", ""), key="ep_name")

    # ── Existing farms (edit + delete) ──
    st.markdown("---")
    st.subheader(f"🏡 {T('your_farms')}")

    # Track which farms to delete via session state
    if "ep_delete_set" not in st.session_state:
        st.session_state.ep_delete_set = set()

    updated_farms = []
    for i, farm in enumerate(farms):
        farm_label = farm.get("farm_name", f"Farm {i+1}")
        is_deleted = i in st.session_state.ep_delete_set

        if is_deleted:
            # Show as struck-out / removed card
            st.markdown(
                f"<div style='background:#ffebee;border:1.5px solid #ef9a9a;"
                f"border-radius:10px;padding:12px 16px;margin-bottom:8px;"
                f"color:#c62828;font-weight:600'>🗑️ {farm_label} — {T('marked_delete')}</div>",
                unsafe_allow_html=True
                )
            undo_col, _ = st.columns([1, 4])
            with undo_col:
                if st.button(f"↩ {T('undo')}", key=f"ep_undo_{i}"):
                    st.session_state.ep_delete_set.discard(i)
                    st.experimental_rerun()
        else:
            with st.expander(f"✏️ {farm_label}", expanded=False):
                fd = farm_form(prefix=f"ep_farm{i}", existing=farm)
                updated_farms_entry = fd

                st.markdown("")
                del_col, _ = st.columns([1, 4])
                with del_col:
                    if st.button(f"🗑️ {T('delete_farm')}", key=f"ep_del_{i}",
                                 use_container_width=True):
                        if len(farms) - len(st.session_state.ep_delete_set) <= 1:
                            st.error(f"❌ {T('keep_one_farm')}")
                        else:
                            st.session_state.ep_delete_set.add(i)
                            st.experimental_rerun()
            # Store updated data
            updated_farms.append((i, updated_farms_entry if not is_deleted else None))
            continue

        updated_farms.append((i, None))  # deleted

    # ── Add new farm ──
    st.markdown("---")
    if st.checkbox(f"➕ {T('add_new_farm')}", key="ep_add_farm"):
        st.markdown(f"#### 🏡 {T('new_farm_details')}")
        new_farm_data = farm_form(prefix="ep_newfarm")
        add_new = True
    else:
        new_farm_data = None
        add_new = False

    # ── Save ──
    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button(f"💾 {T('save_changes')}", use_container_width=True):
            errors = []
            if not new_name.strip():
                errors.append(f"❌ {T('enter_name')}")

            # Collect non-deleted farms
            kept_farms = []
            for i, farm in enumerate(farms):
                if i in st.session_state.ep_delete_set:
                    continue  # skip deleted
                # Find updated version
                updated_fd = next((fd for idx, fd in updated_farms if idx == i and fd), None)
                if updated_fd:
                    kept_farms.append(updated_fd)
                else:
                    kept_farms.append(farm)

            # Validate kept farms
            for i, fd in enumerate(kept_farms):
                if not fd.get("farm_name", "").strip():
                    errors.append(f"❌ Farm {i+1}: Enter a farm name.")
                if fd["farm_area"] <= 0:
                    errors.append(f"❌ Farm {i+1}: Enter farm area.")
                if fd.get("lat") is None:
                    errors.append(f"❌ Farm {i+1}: Set location.")
                if not fd.get("crop"):
                    errors.append(f"❌ Farm {i+1}: Select a crop.")
                if not fd.get("water_sources"):
                    errors.append(f"❌ Farm {i+1}: Select water sources.")

            # Validate new farm if being added
            if add_new and new_farm_data:
                if not new_farm_data["farm_name"].strip():
                    errors.append("❌ New farm: Enter a farm name.")
                elif new_farm_data["farm_area"] <= 0:
                    errors.append("❌ New farm: Enter farm area.")
                elif new_farm_data["lat"] is None:
                    errors.append("❌ New farm: Set location.")
                elif not new_farm_data["crop"]:
                    errors.append("❌ New farm: Select a crop.")
                elif not new_farm_data["water_sources"]:
                    errors.append("❌ New farm: Select water sources.")
                else:
                    kept_farms.append(new_farm_data)

            # Must have at least 1 farm
            if len(kept_farms) == 0:
                errors.append("❌ You must keep at least one farm.")

            # Duplicate detection
            if not errors:
                seen = []
                for i, fd in enumerate(kept_farms):
                    if is_duplicate_farm(fd, seen):
                        errors.append(
                            f"❌ Farm \"{fd.get('farm_name', i+1)}\" is a duplicate — "
                            f"same name or same location as another farm."
                        )
                    else:
                        seen.append(fd)

            if errors:
                for e in errors: st.error(e)
            else:
                profile["name"]  = new_name.strip()
                profile["farms"] = kept_farms
                upsert_user(phone, profile)
                st.session_state.profile      = profile
                st.session_state.active_farm  = 0
                st.session_state.ep_delete_set = set()
                st.session_state.page = "main"
                st.experimental_rerun()

    with c2:
        if st.button(f"← {T('back_dashboard')}", use_container_width=True):
            st.session_state.ep_delete_set = set()
            st.session_state.page = "main"
            st.experimental_rerun()


# ════════════════════════════════════════════
#  ROUTER
# ════════════════════════════════════════════
if st.session_state.phone is None:
    remembered_phone = load_last_login()

    if remembered_phone:
        remembered_user = get_user(remembered_phone)

        if remembered_user:
            st.session_state.phone = remembered_phone
            st.session_state.profile = remembered_user
            st.session_state.page = "main"
PAGE = st.session_state.page

if PAGE == "login":
    page_login()
elif PAGE == "signup":
    page_signup()
elif PAGE == "main":
    mp = os.path.join(BASE_DIR, "model.pkl")
    if os.path.exists(mp):
        model = joblib.load(mp)
    page_main()
elif PAGE == "edit_profile":
    page_edit_profile()
