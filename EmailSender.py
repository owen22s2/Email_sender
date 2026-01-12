import smtplib
import requests
import os
from email.mime.text import MIMEText

# ---------- CONFIG ----------
EMAIL = "owensstas@gmail.com"
PASSWORD = os.getenv("EMAIL_PASS")
RECEIVERS = ["owensstas@gmail.com"]

# Oostzaan
LAT = 52.4389
LON = 4.8746

COLD_TEMP = 15
FREEZING_TEMP = 0
WINDY_SPEED = 30

STATE_FILE = "last_temp.txt"

if not PASSWORD:
    raise RuntimeError("EMAIL_PASS not set")


def map_weather(code):
    if code == 0:
        return "clear"
    if code in [1, 2, 3]:
        return "clouds"
    if code in [51, 53, 55, 61, 63, 65]:
        return "rain"
    if code in [71, 73, 75]:
        return "snow"
    if code in [95, 96, 99]:
        return "thunder"
    return "clouds"


def get_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current_weather": True
    }

    data = requests.get(url, params=params, timeout=10).json()
    cw = data["current_weather"]

    return {
        "temp": cw["temperature"],
        "condition": map_weather(cw["weathercode"]),
        "wind": cw["windspeed"]
    }


def feels_like(temp, wind):
    return round(temp - (wind * 0.1), 1)


def weather_advice(temp, condition, wind):
    if condition == "thunder":
        return "⚡ Stay indoors, thunderstorm warning!"
    if condition == "rain":
        return "🌧️ Bring a jacket or umbrella"
    if condition == "snow":
        return "❄️ Wear gloves and a hat"
    if temp <= FREEZING_TEMP:
        return "🥶 Dress warm, freezing outside"
    if wind >= WINDY_SPEED:
        return "💨 Very windy, wear something windproof"
    if temp > 30:
        return "🥵 Hot, dress comfortably"
    if temp >= 22:
        return "😎 Nice weather, light clothing is fine"
    if temp >= 12:
        return "🧥 Kinda cold, wear a sweater"
    if temp >= 8:
        return "Cold, put on some warm clothes"   
    return "🆒 Cool weather, wear a jacket and some gloves"




def send_weather_email():
    w = get_weather()

    temp = w["temp"]
    condition = w["condition"]
    wind = w["wind"]
    temp_state = (
        "freezing" if temp <= FREEZING_TEMP
        else "cold" if temp < COLD_TEMP
        else "warm"
    )
 # Add emojis to the subject
    emoji_map = {
        "clear": "☀️",
        "clouds": "☁️",
        "rain": "🌧️",
        "snow": "❄️",
        "thunder": "⚡"
    }
    weather_emoji = emoji_map.get(condition, "🌤️") 
    wind_state = "windy" if wind >= WINDY_SPEED else "calm"

    feels = feels_like(temp, wind)
    advice = weather_advice(temp, condition, wind)

    subject = f" {weather_emoji}Update | {temp}°C | {condition.upper()}"

    body = (
        f"Location: Oostzaan\n\n"
        f"Temperature: {temp}°C ({temp_state})\n"
        f"Feels like: {feels}°C\n"
        f"Condition: {condition}\n"
        f"Wind: {wind} km/h ({wind_state})\n\n"
        f"Advice: {advice}"
    )

    msg = MIMEText(body)
    msg["From"] = EMAIL
    msg["Subject"] = subject

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(EMAIL, PASSWORD)

    for r in RECEIVERS:
        msg["To"] = r
        server.send_message(msg)

    server.quit()


send_weather_email()

#script made with ai

