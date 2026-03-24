# 🌦️ Weather Chatbot

A Streamlit-based weather chatbot with an **Ocean Teal & Blue** theme that fetches real-time weather data and reads it aloud in your chosen language.

---

## ✨ Features

- 🌡️ Real-time weather data via **OpenWeatherMap API**
- 📊 Live dashboard with Temperature, Humidity, Wind Speed, Condition & Pressure
- 🔊 Text-to-Speech reply in **Hindi, Gujarati, French, or Spanish**
- 🎨 Ocean Teal & Blue dark theme

---

## 🚀 Getting Started

### 1. Clone / Download the project
```bash
git clone <your-repo-url>
cd weather-chatbot
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Get a free API key
Sign up at [openweathermap.org](https://openweathermap.org/api) and copy your API key.

### 4. Run the app
```bash
streamlit run app.py
```

### 5. Use the app
1. Paste your OpenWeatherMap API key in the **sidebar**
2. Select your preferred **reply language**
3. Type a city name in the chat (e.g. *What's the weather in Ahmedabad?*)

---

## 📁 Project Structure

```
weather-chatbot/
├── app.py            # Main Streamlit application
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

---

## 📦 Dependencies

| Package      | Purpose                        |
|-------------|--------------------------------|
| `streamlit`  | Web UI framework               |
| `requests`   | HTTP calls to Weather API      |
| `gTTS`       | Google Text-to-Speech          |

---

## 🔑 Environment Note

Your API key is entered at runtime via the sidebar — it is **never stored** in the code or committed to version control.

---

## 📄 License

MIT License — free to use and modify.
