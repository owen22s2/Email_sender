import smtplib
import requests
import os
from datetime import datetime
from email.mime.text import MIMEText

# ---------- CONFIG ----------
EMAIL = "owensstas@gmail.com"
PASSWORD = os.getenv("EMAIL_PASS")  # secret
RECEIVERS = ["owensstas@gmail.com"]

LAT = 52.3676
LON = 4.9041

COLD_TEMP = 15
FREEZING_TEMP = 0
WINDY_SPEED = 30

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

    wind_state = "windy" if wind >= WINDY_SPEED else "calm"

    subject = f"Weather | {temp_state.upper()} | {condition.upper()}"

    body = (
        f"Time: {datetime.now()}\n"
        f"Temperature: {temp}°C ({temp_state})\n"
        f"Condition: {condition}\n"
        f"Wind: {wind} km/h ({wind_state})"
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
