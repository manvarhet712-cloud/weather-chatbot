import re
import tempfile
import streamlit as st
import requests
from gtts import gTTS
from deep_translator import GoogleTranslator

st.set_page_config(page_title="Weather Chatbot", page_icon="🌤️", layout="wide")

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a1628 0%, #0d2137 50%, #0a2744 100%);
        color: #e0f4f8;
    }
    .main .block-container { background: transparent; padding-top: 2rem; }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d2137 0%, #0a1e30 100%);
        border-right: 1px solid #1a4a6e;
    }
    [data-testid="stSidebar"] * { color: #b0dce8 !important; }
    [data-testid="stSidebar"] input {
        background: #0d2f47 !important; border: 1px solid #1e6091 !important;
        color: #e0f4f8 !important; border-radius: 8px;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: #0d2f47 !important; border: 1px solid #1e6091 !important;
        color: #e0f4f8 !important; border-radius: 8px;
    }
    h1 {
        background: linear-gradient(90deg, #00c9d4, #0ea5e9, #38bdf8);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; font-size: 2.4rem !important;
        font-weight: 800 !important; letter-spacing: -0.5px;
    }
    h3 { color: #38bdf8 !important; font-weight: 700 !important; }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, #0d2f47 0%, #0a3a57 100%);
        border: 1px solid #1e6091; border-radius: 14px;
        padding: 1.2rem 1.4rem !important;
        box-shadow: 0 4px 20px rgba(0, 180, 220, 0.15);
    }
    [data-testid="metric-container"] label,
    [data-testid="metric-container"] [data-testid="stMetricLabel"] p {
        color: #7dd3fc !important; font-size: 0.85rem !important;
        font-weight: 600 !important; letter-spacing: 0.5px;
    }
    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] > div {
        color: #ffffff !important; font-size: 1.8rem !important;
        font-weight: 800 !important; -webkit-text-fill-color: #ffffff !important;
    }
    [data-testid="stMetricDelta"] {
        color: #00c9d4 !important; font-size: 0.82rem !important;
        -webkit-text-fill-color: #00c9d4 !important;
    }
    [data-testid="stChatMessage"] {
        background: linear-gradient(135deg, #0d2f47 0%, #0a3a57 100%) !important;
        border: 1px solid #1e6091; border-radius: 14px !important; margin-bottom: 0.8rem;
    }
    [data-testid="stChatMessage"] p { color: #e0f4f8 !important; }
    [data-testid="stChatInputTextArea"] {
        background: #0d2f47 !important; border: 1px solid #1e6091 !important;
        color: #e0f4f8 !important; border-radius: 12px !important;
    }
    [data-testid="stChatInputTextArea"]:focus {
        border-color: #00c9d4 !important;
        box-shadow: 0 0 0 3px rgba(0, 201, 212, 0.2) !important;
    }
    hr { border-color: #1e6091 !important; opacity: 0.6; }
    .stSpinner > div { border-top-color: #00c9d4 !important; }
    audio { filter: invert(1) hue-rotate(180deg); border-radius: 8px; width: 100%; }
    [data-testid="stAlert"] {
        background: rgba(220, 38, 38, 0.15) !important;
        border: 1px solid rgba(220, 38, 38, 0.4) !important;
        border-radius: 10px !important; color: #fca5a5 !important;
    }
    strong { color: #38bdf8 !important; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: #0a1628; }
    ::-webkit-scrollbar-thumb { background: #1e6091; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #00c9d4; }

    div[data-testid="stButton"] > button {
        background: rgba(14, 165, 233, 0.07) !important;
        border: 1px solid #1e6091 !important;
        border-radius: 20px !important;
        color: #7dd3fc !important;
        font-size: 0.76rem !important;
        padding: 0.32rem 0.7rem !important;
        width: 100% !important;
        text-align: left !important;
        margin-bottom: 4px !important;
        transition: all 0.2s ease !important;
        white-space: normal !important;
        height: auto !important;
        line-height: 1.4 !important;
    }
    div[data-testid="stButton"] > button:hover {
        background: rgba(0, 201, 212, 0.15) !important;
        border-color: #00c9d4 !important;
        color: #00c9d4 !important;
        transform: translateX(4px) !important;
    }
    .forecast-row {
        display: flex; align-items: center; gap: 12px;
        background: rgba(13,47,71,0.6); border: 1px solid #1e6091;
        border-radius: 10px; padding: 10px 14px; margin-bottom: 6px;
    }
    .forecast-time     { color: #7dd3fc; font-size: 0.8rem; min-width: 130px; }
    .forecast-temp     { color: #fff; font-weight: 700; min-width: 70px; }
    .forecast-desc     { color: #b0dce8; font-size: 0.85rem; flex: 1; }
    .forecast-rain     { color: #38bdf8; font-size: 0.82rem; min-width: 80px; }
    .forecast-humidity { color: #a78bfa; font-size: 0.82rem; min-width: 60px; }
    .forecast-wind     { color: #6ee7b7; font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)

st.title("🌦️ Weather Chatbot")

if "triggered_question" not in st.session_state:
    st.session_state.triggered_question = ""

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    api_key = st.text_input("Enter OpenWeatherMap API Key", type="password")
    language = st.selectbox(
        "Reply Language",
        ["en", "hi", "gu", "fr", "es"],
        format_func=lambda x: {
            "en": "English", "hi": "Hindi", "gu": "Gujarati",
            "fr": "French", "es": "Spanish"
        }[x]
    )

    st.divider()
    st.markdown("### 💬 Quick Questions")
    st.caption("Click a question, then type your city name in the chat!")

    # 🌧️ Rain Prediction
    st.markdown("**🌧️ Rain Prediction**")
    for q in [
        "Will it rain tomorrow in [city]?",
        "Rain prediction for next 2 days in [city]?",
        "How much rainfall in [city] this week?",
        "Chance of rain in [city] next 3 days?",
        "Rain forecast for [city] next 5 days?",
    ]:
        if st.button(q, key=f"r_{q}"):
            st.session_state.triggered_question = q
            st.rerun()

    # 🌡️ Temperature Forecast
    st.markdown("**🌡️ Temperature Forecast**")
    for q in [
        "Max and min temperature in [city] tomorrow?",
        "How hot will [city] be next 3 days?",
        "Temperature forecast for [city] this week?",
        "Temperature trend for [city] next 5 days?",
    ]:
        if st.button(q, key=f"t_{q}"):
            st.session_state.triggered_question = q
            st.rerun()

    # 💧 Humidity & Wind
    st.markdown("**💧 Humidity & Wind**")
    for q in [
        "Humidity forecast for [city] tomorrow?",
        "Is it going to be humid in [city] next 3 days?",
        "Wind speed forecast for [city] this week?",
        "How windy will [city] be tomorrow?",
    ]:
        if st.button(q, key=f"h_{q}"):
            st.session_state.triggered_question = q
            st.rerun()

    # ⛈️ Storm & Thunderstorm
    st.markdown("**⛈️ Storm & Thunderstorm**")
    for q in [
        "Is there a thunderstorm warning for [city] today?",
        "Will there be a storm in [city] next 2 days?",
        "Storm forecast for [city] tomorrow?",
        "Is [city] at risk of thunderstorm this week?",
    ]:
        if st.button(q, key=f"s_{q}"):
            st.session_state.triggered_question = q
            st.rerun()

# ── Helpers ───────────────────────────────────────────────────────────────────
KNOWN_CITIES = [
    "new york", "new delhi", "los angeles", "san francisco", "kuala lumpur",
    "hong kong", "saint petersburg", "rio de janeiro", "buenos aires",
    "mexico city", "cape town",
]

def extract_city(text):
    lower = text.lower()
    if "[city]" in lower:
        return None
    for city in KNOWN_CITIES:
        if city in lower:
            return city.title()
    match = re.search(r"\b(?:in|for|at)\s+([A-Za-z]+(?: [A-Za-z]+){0,2}?)[\?\.\!,]?$", text, re.IGNORECASE)
    if match:
        return match.group(1).strip().title()
    last_word = re.sub(r"[^\w]", "", text.split()[-1])
    return last_word.title()

def detect_intent(text):
    t = text.lower()
    if any(w in t for w in ["thunder", "storm", "lightning"]):       return "storm"
    if any(w in t for w in ["rain", "drizzle", "shower", "rainfall"]): return "rain"
    if any(w in t for w in ["humid", "humidity", "moisture"]):        return "humidity"
    if any(w in t for w in ["wind", "windy", "gust"]):                return "wind"
    if any(w in t for w in ["temp", "hot", "cold", "max", "min", "high", "low", "degree", "heat"]): return "temperature"
    if any(w in t for w in ["forecast", "next", "tomorrow", "days", "week", "prediction"]): return "forecast"
    return "current"

def extract_days(text):
    m = re.search(r"next\s+(\d+)\s+day", text, re.IGNORECASE)
    if m: return int(m.group(1))
    if "tomorrow" in text.lower(): return 1
    if "week"     in text.lower(): return 7
    return 2

def fetch_forecast(city, key, days):
    cnt = min(days * 8, 40)
    url = (f"http://api.openweathermap.org/data/2.5/forecast"
           f"?q={city}&appid={key}&units=metric&cnt={cnt}")
    return requests.get(url).json()

def emoji_for(desc):
    d = desc.lower()
    if "thunder" in d: return "⛈️"
    if "drizzle" in d: return "🌦️"
    if "rain"    in d: return "🌧️"
    if "snow"    in d: return "❄️"
    if "mist"    in d or "fog" in d: return "🌫️"
    if "cloud"   in d: return "☁️"
    if "clear"   in d: return "☀️"
    return "🌡️"

def show_forecast(fdata, city, intent, days):
    items = fdata.get("list", [])
    if not items:
        st.warning("No forecast data available.")
        return

    titles = {
        "rain":        f"🌧️ Rain Prediction — Next {days} Day(s) · {city}",
        "temperature": f"🌡️ Temperature Forecast — Next {days} Day(s) · {city}",
        "humidity":    f"💧 Humidity Forecast — Next {days} Day(s) · {city}",
        "wind":        f"🌬️ Wind Forecast — Next {days} Day(s) · {city}",
        "storm":       f"⛈️ Storm / Thunderstorm Forecast — Next {days} Day(s) · {city}",
    }
    st.subheader(titles.get(intent, f"📅 Forecast — Next {days} Day(s) · {city}"))
    st.divider()

    rain_total = 0.0
    storm_slots = []
    temps = []
    rows_html = ""

    for item in items:
        dt   = item["dt_txt"]
        temp = round(item["main"]["temp"], 1)
        tmax = round(item["main"]["temp_max"], 1)
        tmin = round(item["main"]["temp_min"], 1)
        hum  = item["main"]["humidity"]
        wnd  = item["wind"]["speed"]
        desc = item["weather"][0]["description"].title()
        emj  = emoji_for(desc)
        rain = item.get("rain", {}).get("3h", 0)
        rain_total += rain
        temps.append(temp)
        if "thunder" in desc.lower() or "storm" in desc.lower():
            storm_slots.append(dt)

        if intent == "rain":
            rs = f"🌧️ {rain:.1f} mm" if rain > 0 else "—"
            rows_html += f'<div class="forecast-row"><span class="forecast-time">🕐 {dt}</span><span class="forecast-temp">{temp}°C</span><span class="forecast-desc">{emj} {desc}</span><span class="forecast-rain">{rs}</span></div>'

        elif intent == "temperature":
            rows_html += f'<div class="forecast-row"><span class="forecast-time">🕐 {dt}</span><span class="forecast-temp">{temp}°C</span><span class="forecast-desc">🔺 {tmax}°C &nbsp;🔻 {tmin}°C</span><span class="forecast-desc">{emj} {desc}</span></div>'

        elif intent == "humidity":
            rows_html += f'<div class="forecast-row"><span class="forecast-time">🕐 {dt}</span><span class="forecast-temp">{temp}°C</span><span class="forecast-desc">{emj} {desc}</span><span class="forecast-humidity">💧 {hum}%</span></div>'

        elif intent == "wind":
            rows_html += f'<div class="forecast-row"><span class="forecast-time">🕐 {dt}</span><span class="forecast-temp">{temp}°C</span><span class="forecast-desc">{emj} {desc}</span><span class="forecast-wind">🌬️ {wnd} m/s</span></div>'

        elif intent == "storm":
            if "thunder" in desc.lower() or "storm" in desc.lower() or "rain" in desc.lower():
                rows_html += f'<div class="forecast-row"><span class="forecast-time">🕐 {dt}</span><span class="forecast-temp">{temp}°C</span><span class="forecast-desc">{emj} {desc}</span><span class="forecast-rain">⚠️ Alert</span></div>'

        else:
            rs = f"🌧️ {rain:.1f} mm" if rain > 0 else ""
            rows_html += f'<div class="forecast-row"><span class="forecast-time">🕐 {dt}</span><span class="forecast-temp">{temp}°C</span><span class="forecast-desc">{emj} {desc}</span><span class="forecast-rain">{rs}</span></div>'

    if rows_html:
        st.markdown(rows_html, unsafe_allow_html=True)
    elif intent == "storm":
        st.success(f"✅ No storm/thunderstorm found for **{city}** in the next {days} day(s).")

    st.divider()

    # Summary + spoken text
    spoken = ""
    if intent == "rain":
        if rain_total > 0:
            st.warning(f"🌧️ Rain expected — **{rain_total:.1f} mm** total over {days} day(s). Carry an umbrella!")
            spoken = f"Rain is expected in {city} over the next {days} days, totalling {rain_total:.1f} millimetres. Carry an umbrella."
        else:
            st.success(f"☀️ No significant rain expected in **{city}** over the next {days} day(s).")
            spoken = f"No significant rain is expected in {city} over the next {days} days."

    elif intent == "temperature" and temps:
        st.info(f"🌡️ Temperatures will range from **{min(temps):.1f}°C** to **{max(temps):.1f}°C** over {days} day(s).")
        spoken = f"In {city}, temperatures will range from {min(temps):.1f} to {max(temps):.1f} degrees over the next {days} days."

    elif intent == "humidity":
        humids = [i["main"]["humidity"] for i in items]
        avg_h  = round(sum(humids) / len(humids))
        level  = "high" if avg_h > 70 else "moderate" if avg_h > 40 else "low"
        st.info(f"💧 Average humidity: **{avg_h}%** ({level}) over {days} day(s).")
        spoken = f"The average humidity in {city} over the next {days} days is {avg_h} percent, which is {level}."

    elif intent == "wind":
        winds = [i["wind"]["speed"] for i in items]
        avg_w = round(sum(winds) / len(winds), 1)
        level = "strong" if avg_w > 10 else "moderate" if avg_w > 5 else "light"
        st.info(f"🌬️ Average wind speed: **{avg_w} m/s** ({level} winds) over {days} day(s).")
        spoken = f"Wind speeds in {city} will average {avg_w} metres per second over the next {days} days, which is {level}."

    elif intent == "storm":
        if storm_slots:
            st.error(f"⛈️ **Storm/Thunderstorm** detected in {len(storm_slots)} slot(s)! Stay safe.")
            spoken = f"Warning: Thunderstorm conditions are expected in {city} over the next {days} days. Please stay safe."
        else:
            st.success(f"✅ No storm expected in **{city}** over the next {days} day(s).")
            spoken = f"No storm or thunderstorm is expected in {city} over the next {days} days."

    if spoken:
        try:
            if language != "en":
                spoken = GoogleTranslator(source="en", target=language).translate(spoken)
            tts = gTTS(text=spoken, lang=language)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                tts.save(tmp.name)
                st.audio(tmp.name, format="audio/mp3")
        except Exception as e:
            st.warning("Audio could not be generated: " + str(e))

# ── Input resolution ──────────────────────────────────────────────────────────
typed_input = st.chat_input("Type your weather question with city name… e.g. Will it rain in Ahmedabad next 2 days?")

if typed_input:
    user_input = typed_input
    st.session_state.triggered_question = ""
elif st.session_state.triggered_question:
    user_input = st.session_state.triggered_question
else:
    user_input = None

# If chip has [city] placeholder, prompt user to retype with city
if user_input and "[city]" in user_input:
    with st.chat_message("user"):
        st.write(user_input)
    with st.chat_message("assistant"):
        example = user_input.replace("[city]", "Ahmedabad")
        st.info(f"🏙️ Please retype this question with your **city name** in the chat box below!\n\n**Example:** `{example}`")
    st.session_state.triggered_question = ""
    user_input = None

# ── Main processing ───────────────────────────────────────────────────────────
if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        if not api_key:
            st.error("Please enter your OpenWeatherMap API key in the sidebar first!")
        else:
            with st.spinner("Fetching weather data..."):
                city_name = extract_city(user_input)
                intent    = detect_intent(user_input)

                if not city_name:
                    st.error("Could not detect a city. Please include a city name in your question.")

                elif intent in ("rain", "temperature", "humidity", "wind", "storm", "forecast"):
                    days = extract_days(user_input)
                    fdata = fetch_forecast(city_name, api_key, days)
                    if str(fdata.get("cod")) == "200":
                        show_forecast(fdata, city_name, intent, days)
                    else:
                        st.error(f"City not found: **{city_name}**. {fdata.get('message','').capitalize()}. Please try again!")

                else:
                    # Current weather
                    r    = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}&units=metric")
                    data = r.json()
                    if data.get("cod") == 200:
                        temp       = round(data["main"]["temp"], 1)
                        desc       = data["weather"][0]["description"]
                        humidity   = data["main"]["humidity"]
                        feels_like = round(data["main"]["feels_like"], 1)
                        wind_speed = data["wind"]["speed"]
                        pressure   = data["main"]["pressure"]

                        st.subheader("📍 Weather Dashboard — " + city_name)
                        st.divider()
                        col1, col2, col3 = st.columns(3)
                        col1.metric("🌡️ Temperature", f"{temp}°C", f"Feels like {feels_like}°C")
                        col2.metric("💧 Humidity",    f"{humidity}%")
                        col3.metric("🌬️ Wind Speed",  f"{wind_speed} m/s")
                        col4, col5 = st.columns(2)
                        col4.metric("🌤️ Condition", desc.title())
                        col5.metric("🔵 Pressure",  f"{pressure} hPa")
                        st.divider()

                        reply = f"City: {city_name}. Temperature: {temp} degrees Celsius. Weather: {desc}. Humidity: {humidity} percent."
                        st.write("🌡️ **" + reply + "**")

                        try:
                            spoken = reply
                            if language != "en":
                                spoken = GoogleTranslator(source="en", target=language).translate(reply)
                            tts = gTTS(text=spoken, lang=language)
                            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                                tts.save(tmp.name)
                                st.audio(tmp.name, format="audio/mp3")
                        except Exception as e:
                            st.warning("Audio could not be generated: " + str(e))
                    else:
                        st.error(f"City not found: {city_name}. {data.get('message','').capitalize()}. Please try again!")

    st.session_state.triggered_question = ""
