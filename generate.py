#!/usr/bin/env python3
"""
Genera una pàgina web amb la previsió del temps a Cabrils
i recomanacions de roba per a tota la família.
"""

import datetime
import json
import os
import sys

import requests

# Cabrils coordinates
LAT = 41.5264
LON = 2.3722
LOCATION = "Cabrils"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def fetch_weather():
    """Fetch current weather data from Open-Meteo API."""
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current": ",".join([
            "temperature_2m",
            "apparent_temperature",
            "is_day",
            "rain",
            "cloud_cover",
            "wind_speed_10m",
            "weather_code",
        ]),
        "daily": ",".join([
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_probability_max",
            "weather_code",
        ]),
        "timezone": "Europe/Madrid",
        "forecast_days": 1,
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def weather_code_description(code):
    """Return Catalan description for WMO weather codes."""
    descriptions = {
        0: ("Cel serè", "sunny"),
        1: ("Majoritàriament serè", "sunny"),
        2: ("Parcialment ennuvolat", "cloudy"),
        3: ("Ennuvolat", "cloudy"),
        45: ("Boira", "foggy"),
        48: ("Boira gelada", "foggy"),
        51: ("Plugim lleugera", "rainy"),
        53: ("Plugim moderada", "rainy"),
        55: ("Plugim intensa", "rainy"),
        61: ("Pluja lleugera", "rainy"),
        63: ("Pluja moderada", "rainy"),
        65: ("Pluja intensa", "rainy"),
        71: ("Neu lleugera", "snowy"),
        73: ("Neu moderada", "snowy"),
        75: ("Neu intensa", "snowy"),
        80: ("Ruixats lleugers", "rainy"),
        81: ("Ruixats moderats", "rainy"),
        82: ("Ruixats intensos", "rainy"),
        85: ("Neu lleugera", "snowy"),
        86: ("Neu intensa", "snowy"),
        95: ("Tempesta", "stormy"),
        96: ("Tempesta amb calamarsa", "stormy"),
        99: ("Tempesta amb calamarsa forta", "stormy"),
    }
    return descriptions.get(code, ("Desconegut", "cloudy"))


def get_background_style(weather_type, is_day):
    """Return CSS background based on weather type and time of day."""
    backgrounds = {
        ("sunny", True): (
            "linear-gradient(135deg, #74b9ff 0%, #0984e3 40%, #fdcb6e 100%)",
            "#0984e3",
        ),
        ("sunny", False): (
            "linear-gradient(135deg, #2d3436 0%, #636e72 40%, #dfe6e9 100%)",
            "#2d3436",
        ),
        ("cloudy", True): (
            "linear-gradient(135deg, #b2bec3 0%, #636e72 50%, #dfe6e9 100%)",
            "#636e72",
        ),
        ("cloudy", False): (
            "linear-gradient(135deg, #2d3436 0%, #636e72 100%)",
            "#2d3436",
        ),
        ("rainy", True): (
            "linear-gradient(135deg, #636e72 0%, #2d3436 50%, #74b9ff 100%)",
            "#636e72",
        ),
        ("rainy", False): (
            "linear-gradient(135deg, #2d3436 0%, #636e72 100%)",
            "#2d3436",
        ),
        ("foggy", True): (
            "linear-gradient(135deg, #dfe6e9 0%, #b2bec3 50%, #636e72 100%)",
            "#b2bec3",
        ),
        ("foggy", False): (
            "linear-gradient(135deg, #636e72 0%, #2d3436 100%)",
            "#636e72",
        ),
        ("snowy", True): (
            "linear-gradient(135deg, #dfe6e9 0%, #b2bec3 50%, #74b9ff 100%)",
            "#b2bec3",
        ),
        ("snowy", False): (
            "linear-gradient(135deg, #636e72 0%, #2d3436 50%, #dfe6e9 100%)",
            "#636e72",
        ),
        ("stormy", True): (
            "linear-gradient(135deg, #2d3436 0%, #636e72 30%, #fdcb6e 100%)",
            "#2d3436",
        ),
        ("stormy", False): (
            "linear-gradient(135deg, #2d3436 0%, #636e72 100%)",
            "#2d3436",
        ),
    }
    return backgrounds.get(
        (weather_type, is_day),
        backgrounds[("cloudy", True)],
    )


def weather_emoji(weather_type, is_day):
    """Return emoji for the weather condition."""
    emojis = {
        ("sunny", True): "☀️",
        ("sunny", False): "🌙",
        ("cloudy", True): "⛅",
        ("cloudy", False): "☁️",
        ("rainy", True): "🌧️",
        ("rainy", False): "🌧️",
        ("foggy", True): "🌫️",
        ("foggy", False): "🌫️",
        ("snowy", True): "❄️",
        ("snowy", False): "❄️",
        ("stormy", True): "⛈️",
        ("stormy", False): "⛈️",
    }
    return emojis.get((weather_type, is_day), "🌤️")


def recommend_clothing(temp, feels_like, is_raining, is_sunny, person):
    """
    Generate clothing recommendations in Catalan.
    person: 'dona', 'home', 'nena3', 'nen6'
    """
    # Adjust effective temperature based on person type
    if person == "dona":
        # Fredulica: feels 3 degrees colder
        effective = feels_like - 3
    elif person == "home":
        # Not cold-sensitive: use feels_like directly
        effective = feels_like
    elif person in ("nena3", "nen6"):
        # Children: feels 1 degree colder (more sensitive)
        effective = feels_like - 1
    else:
        effective = feels_like

    items = []

    # Temperature-based layers
    if effective < 5:
        if person == "dona":
            items.extend([
                "Abric gruixut d'hivern",
                "Jersei de llana gruixut",
                "Samarreta interior tèrmica",
                "Pantalons gruixuts o llana",
                "Bufanda gruixuda",
                "Guants",
                "Gorro de llana",
                "Botes d'hivern",
            ])
        elif person == "home":
            items.extend([
                "Abric d'hivern",
                "Jersei o dessuadora gruixuda",
                "Samarreta interior",
                "Pantalons llargs",
                "Bufanda",
                "Sabates tancades",
            ])
        elif person == "nena3":
            items.extend([
                "Abric gruixut amb caputxa",
                "Jersei de llana",
                "Samarreta interior tèrmica",
                "Pantalons gruixuts",
                "Bufanda",
                "Guants de manyopla",
                "Gorro",
                "Botes calentes",
            ])
        else:  # nen6
            items.extend([
                "Abric gruixut",
                "Jersei de llana",
                "Samarreta interior",
                "Pantalons gruixuts",
                "Bufanda",
                "Guants",
                "Gorro",
                "Botes calentes",
            ])
    elif effective < 10:
        if person == "dona":
            items.extend([
                "Abric mitjà o jaqueta gruixuda",
                "Jersei de llana",
                "Samarreta interior",
                "Pantalons llargs gruixuts",
                "Bufanda lleugera",
                "Botes o sabates tancades",
            ])
        elif person == "home":
            items.extend([
                "Jaqueta mitjana",
                "Jersei o dessuadora",
                "Samarreta",
                "Pantalons llargs",
                "Sabates tancades",
            ])
        elif person == "nena3":
            items.extend([
                "Jaqueta gruixuda amb caputxa",
                "Jersei",
                "Samarreta interior",
                "Pantalons llargs gruixuts",
                "Sabates tancades",
                "Gorro lleuger",
            ])
        else:  # nen6
            items.extend([
                "Jaqueta gruixuda",
                "Jersei",
                "Samarreta interior",
                "Pantalons llargs",
                "Sabates tancades",
            ])
    elif effective < 15:
        if person == "dona":
            items.extend([
                "Jaqueta lleugera o càrdigan gruixut",
                "Jersei prim o samarreta màniga llarga",
                "Pantalons llargs",
                "Sabates tancades",
            ])
        elif person == "home":
            items.extend([
                "Jaqueta lleugera o dessuadora",
                "Samarreta màniga llarga",
                "Pantalons llargs",
                "Sabates",
            ])
        elif person == "nena3":
            items.extend([
                "Jaqueta lleugera",
                "Samarreta màniga llarga",
                "Pantalons llargs",
                "Sabates tancades",
            ])
        else:  # nen6
            items.extend([
                "Jaqueta lleugera",
                "Samarreta màniga llarga",
                "Pantalons llargs",
                "Sabates tancades o esportives",
            ])
    elif effective < 20:
        if person == "dona":
            items.extend([
                "Càrdigan o jaqueta fina",
                "Samarreta màniga llarga o curta",
                "Pantalons llargs o texans",
                "Sabates còmodes",
            ])
        elif person == "home":
            items.extend([
                "Samarreta màniga curta",
                "Pantalons llargs o curts",
                "Sabates o esportives",
            ])
        elif person == "nena3":
            items.extend([
                "Samarreta màniga llarga o curta",
                "Pantalons llargs lleugers",
                "Sabates còmodes",
            ])
        else:  # nen6
            items.extend([
                "Samarreta màniga curta",
                "Pantalons llargs o curts",
                "Esportives",
            ])
    elif effective < 25:
        if person == "dona":
            items.extend([
                "Samarreta màniga curta",
                "Pantalons llargs lleugers o faldilla",
                "Sandàlies o sabates lleugeres",
            ])
        elif person == "home":
            items.extend([
                "Samarreta màniga curta",
                "Pantalons curts o llargs lleugers",
                "Sandàlies o esportives",
            ])
        elif person == "nena3":
            items.extend([
                "Samarreta màniga curta",
                "Pantalons curts",
                "Sandàlies o sabates",
            ])
        else:  # nen6
            items.extend([
                "Samarreta màniga curta",
                "Pantalons curts",
                "Sandàlies o esportives",
            ])
    else:  # >= 25
        if person == "dona":
            items.extend([
                "Samarreta lleugera de tirants o màniga curta",
                "Pantalons curts o faldilla lleugera",
                "Sandàlies",
            ])
        elif person == "home":
            items.extend([
                "Samarreta màniga curta lleugera",
                "Pantalons curts",
                "Sandàlies",
            ])
        elif person == "nena3":
            items.extend([
                "Samarreta màniga curta lleugera",
                "Pantalons curts",
                "Sandàlies",
            ])
        else:  # nen6
            items.extend([
                "Samarreta màniga curta lleugera",
                "Pantalons curts",
                "Sandàlies",
            ])

    # Rain additions
    if is_raining:
        items.append("Paraigua ☔")
        if person in ("nena3", "nen6"):
            items.append("Botes d'aigua")
            items.append("Impermeable amb caputxa")
        elif person == "dona":
            items.append("Impermeable o jaqueta amb caputxa")
        else:
            items.append("Impermeable o jaqueta impermeable")

    # Sun protection
    if is_sunny and effective >= 20:
        items.append("Crema solar 🧴")
        if person in ("nena3", "nen6"):
            items.append("Gorra de sol")
            items.append("Ulleres de sol")
        elif person == "dona":
            items.append("Ulleres de sol")
            items.append("Barret o gorra")
        else:
            items.append("Ulleres de sol")
            items.append("Gorra")

    return items


def person_icon(person):
    """Return icon and name for each family member."""
    icons = {
        "dona": ("👩", "Mare"),
        "home": ("👨", "Pare"),
        "nen6": ("👦", "Nen (6 anys)"),
        "nena3": ("👶", "Nena (3 anys)"),
    }
    return icons.get(person, ("👤", person))


def generate_html(weather_data):
    """Generate the full HTML page."""
    current = weather_data["current"]
    daily = weather_data["daily"]

    temp = current["temperature_2m"]
    feels_like = current["apparent_temperature"]
    is_day = bool(current["is_day"])
    rain = current["rain"]
    cloud_cover = current["cloud_cover"]
    wind_speed = current["wind_speed_10m"]
    weather_code = current["weather_code"]

    temp_max = daily["temperature_2m_max"][0]
    temp_min = daily["temperature_2m_min"][0]
    feels_max = daily["apparent_temperature_max"][0]
    feels_min = daily["apparent_temperature_min"][0]
    precip_prob = daily["precipitation_probability_max"][0]

    desc, weather_type = weather_code_description(weather_code)
    is_raining = rain > 0 or weather_type == "rainy"
    is_sunny = weather_type == "sunny" and cloud_cover < 50

    bg_gradient, bg_color = get_background_style(weather_type, is_day)
    emoji = weather_emoji(weather_type, is_day)

    now = datetime.datetime.now(
        tz=datetime.timezone(datetime.timedelta(hours=1))
    )
    # Use Europe/Madrid offset (CET=+1, CEST=+2)
    # Simple DST check: last Sunday of March to last Sunday of October
    year = now.year
    march_last_sun = 31 - (
        datetime.date(year, 3, 31).weekday() + 1
    ) % 7
    oct_last_sun = 31 - (
        datetime.date(year, 10, 31).weekday() + 1
    ) % 7
    dst_start = datetime.date(year, 3, march_last_sun)
    dst_end = datetime.date(year, 10, oct_last_sun)
    if dst_start <= now.date() <= dst_end:
        offset = datetime.timezone(datetime.timedelta(hours=2))
    else:
        offset = datetime.timezone(datetime.timedelta(hours=1))
    now = datetime.datetime.now(tz=offset)

    update_time = now.strftime("%d/%m/%Y %H:%M")

    people = ["dona", "home", "nen6", "nena3"]
    cards_html = ""
    for person in people:
        icon, name = person_icon(person)
        items = recommend_clothing(
            temp, feels_like, is_raining, is_sunny, person
        )
        items_html = "".join(f"<li>{item}</li>" for item in items)
        cards_html += f"""
        <div class="card">
            <div class="card-header">
                <span class="person-icon">{icon}</span>
                <h2>{name}</h2>
            </div>
            <ul class="clothing-list">
                {items_html}
            </ul>
        </div>
        """

    # Determine text color based on background
    text_color = "#fff" if weather_type in (
        "rainy", "stormy"
    ) or not is_day else "#2d3436"
    header_text_color = "#fff" if not is_day or weather_type in (
        "rainy", "stormy"
    ) else "#2d3436"

    rain_info = ""
    if precip_prob and precip_prob > 0:
        rain_info = f"""
        <div class="weather-detail">
            <span class="detail-icon">🌧️</span>
            <span>Probabilitat de pluja: {precip_prob}%</span>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="ca">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Temps a {LOCATION} - Quina roba portar?</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Press+Start+2P&display=swap" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        /* ===== BASE / SHARED STYLES ===== */
        body {{
            min-height: 100vh;
            background-attachment: fixed;
            transition: font-family 0.3s, background 0.3s, color 0.3s;
        }}

        .weather-bg {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 0;
            overflow: hidden;
            pointer-events: none;
        }}

        .weather-bg .particle {{
            position: absolute;
            border-radius: 50%;
            opacity: 0.3;
            animation: float 6s ease-in-out infinite;
        }}

        @keyframes float {{
            0%, 100% {{ transform: translateY(0) rotate(0deg); }}
            50% {{ transform: translateY(-20px) rotate(180deg); }}
        }}

        .container {{
            position: relative;
            z-index: 1;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            padding: 30px 20px;
        }}

        .weather-emoji {{
            font-size: 4em;
            margin: 15px 0;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
        }}

        .weather-summary {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 12px;
            margin: 20px 0 30px;
            padding: 25px;
        }}

        .weather-detail {{
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
        }}

        .detail-icon {{
            font-size: 1.3em;
        }}

        .temp-main {{
            font-weight: bold;
        }}

        .cards-grid {{
            display: grid;
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            padding-bottom: 12px;
        }}

        .clothing-list {{
            list-style: none;
            padding: 0;
        }}

        .clothing-list li {{
            padding: 8px 12px;
            margin: 4px 0;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            opacity: 0.8;
            font-size: 0.9em;
        }}

        /* ===== STYLE TOGGLE ===== */
        .style-toggle {{
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .style-toggle label {{
            font-size: 0.85em;
            font-weight: 600;
            cursor: pointer;
        }}

        .toggle-switch {{
            position: relative;
            width: 56px;
            height: 28px;
            cursor: pointer;
        }}

        .toggle-switch input {{
            opacity: 0;
            width: 0;
            height: 0;
        }}

        .toggle-slider {{
            position: absolute;
            inset: 0;
            border-radius: 28px;
            transition: background 0.3s;
        }}

        .toggle-slider::before {{
            content: '';
            position: absolute;
            width: 22px;
            height: 22px;
            left: 3px;
            bottom: 3px;
            border-radius: 50%;
            transition: transform 0.3s;
        }}

        .toggle-switch input:checked + .toggle-slider::before {{
            transform: translateX(28px);
        }}

        /* ===== MODERN STYLE (default) ===== */
        body.modern {{
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: {bg_gradient};
            background-color: {bg_color};
            color: {text_color};
        }}

        .modern header {{
            color: {header_text_color};
        }}

        .modern header h1 {{
            font-size: 2.4em;
            margin-bottom: 10px;
            text-shadow: 0 2px 8px rgba(0,0,0,0.15);
            letter-spacing: -0.02em;
        }}

        .modern .weather-desc {{
            font-size: 1.3em;
            margin-bottom: 8px;
        }}

        .modern .temp-main {{
            font-size: 3.2em;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .modern .weather-summary {{
            background: rgba(255,255,255,0.15);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 24px;
            border: 1px solid rgba(255,255,255,0.2);
        }}

        .modern .weather-detail {{
            font-size: 1em;
            background: rgba(255,255,255,0.12);
            border-radius: 14px;
        }}

        .modern .cards-grid {{
            grid-template-columns: repeat(4, 1fr);
        }}

        .modern .card {{
            background: rgba(255,255,255,0.92);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border-radius: 20px;
            padding: 24px;
            color: #2d3436;
            box-shadow: 0 8px 32px rgba(0,0,0,0.08);
            border: 1px solid rgba(255,255,255,0.3);
            transition: transform 0.25s ease, box-shadow 0.25s ease;
        }}

        .modern .card:hover {{
            transform: translateY(-6px);
            box-shadow: 0 16px 48px rgba(0,0,0,0.12);
        }}

        .modern .card-header {{
            border-bottom: 2px solid #f0f0f0;
        }}

        .modern .person-icon {{
            font-size: 2.4em;
        }}

        .modern .card-header h2 {{
            font-size: 1.2em;
            color: #2d3436;
            font-weight: 700;
        }}

        .modern .clothing-list li {{
            background: linear-gradient(90deg, #f8f9fa, #fff);
            border-radius: 10px;
            font-size: 0.9em;
            border-left: 3px solid #74b9ff;
        }}

        .modern .clothing-list li:nth-child(even) {{
            border-left-color: #a29bfe;
        }}

        .modern .toggle-slider {{
            background: rgba(255,255,255,0.3);
            border: 1px solid rgba(255,255,255,0.4);
        }}

        .modern .toggle-slider::before {{
            background: #fff;
            box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        }}

        .modern .toggle-switch input:checked + .toggle-slider {{
            background: rgba(116,185,255,0.6);
        }}

        .modern .style-toggle label {{
            color: {header_text_color};
            text-shadow: 0 1px 3px rgba(0,0,0,0.15);
        }}

        /* ===== RETRO STYLE ===== */
        body.retro {{
            font-family: 'Press Start 2P', monospace;
            background: #1a1a2e;
            color: #0ff;
            image-rendering: pixelated;
        }}

        .retro .weather-bg {{
            display: none;
        }}

        .retro header {{
            color: #0ff;
            border-bottom: 4px dashed #0ff;
            padding-bottom: 20px;
        }}

        .retro header h1 {{
            font-size: 1.2em;
            margin-bottom: 10px;
            color: #ff0;
            text-shadow: 3px 3px 0 #f0f;
            letter-spacing: 0.05em;
        }}

        .retro .weather-desc {{
            font-size: 0.7em;
            margin-bottom: 8px;
            color: #0f0;
        }}

        .retro .temp-main {{
            font-size: 1.6em;
            color: #ff0;
            text-shadow: 2px 2px 0 #f00;
        }}

        .retro .weather-summary {{
            background: #16213e;
            border: 3px solid #0ff;
            border-radius: 0;
            box-shadow: 6px 6px 0 #0ff;
        }}

        .retro .weather-detail {{
            font-size: 0.55em;
            background: #0f3460;
            border: 2px solid #0ff;
            border-radius: 0;
            color: #0ff;
        }}

        .retro .cards-grid {{
            grid-template-columns: repeat(4, 1fr);
        }}

        .retro .card {{
            background: #16213e;
            border: 3px solid #0f0;
            border-radius: 0;
            padding: 20px;
            color: #0ff;
            box-shadow: 6px 6px 0 #0f0;
            transition: transform 0.15s;
        }}

        .retro .card:hover {{
            transform: translate(-3px, -3px);
            box-shadow: 9px 9px 0 #0f0;
        }}

        .retro .card-header {{
            border-bottom: 2px dashed #0f0;
        }}

        .retro .person-icon {{
            font-size: 2em;
        }}

        .retro .card-header h2 {{
            font-size: 0.7em;
            color: #ff0;
        }}

        .retro .clothing-list li {{
            background: #0f3460;
            border-radius: 0;
            font-size: 0.55em;
            border-left: 4px solid #f0f;
            line-height: 1.8;
            color: #0ff;
        }}

        .retro .clothing-list li:nth-child(even) {{
            border-left-color: #0f0;
        }}

        .retro footer {{
            color: #0ff;
            border-top: 4px dashed #0ff;
            margin-top: 20px;
            padding-top: 20px;
        }}

        .retro footer a {{
            color: #ff0 !important;
        }}

        .retro .toggle-slider {{
            background: #0f3460;
            border: 2px solid #0ff;
            border-radius: 0;
        }}

        .retro .toggle-slider::before {{
            background: #0ff;
            border-radius: 0;
            box-shadow: 2px 2px 0 #f0f;
        }}

        .retro .toggle-switch input:checked + .toggle-slider {{
            background: #0f0;
        }}

        .retro .toggle-switch input:checked + .toggle-slider::before {{
            background: #1a1a2e;
        }}

        .retro .style-toggle label {{
            color: #0ff;
            font-size: 0.55em;
        }}

        /* ===== RESPONSIVE: Tablet ===== */
        @media (max-width: 1024px) {{
            .cards-grid {{
                grid-template-columns: repeat(2, 1fr) !important;
            }}
        }}

        /* ===== RESPONSIVE: Mobile ===== */
        @media (max-width: 600px) {{
            .container {{
                padding: 12px;
            }}

            .modern header h1 {{
                font-size: 1.6em;
            }}

            .retro header h1 {{
                font-size: 0.8em;
            }}

            .modern .temp-main {{
                font-size: 2.2em;
            }}

            .retro .temp-main {{
                font-size: 1.2em;
            }}

            .weather-summary {{
                flex-direction: column;
                align-items: center;
                padding: 16px;
                gap: 8px;
            }}

            .cards-grid {{
                grid-template-columns: 1fr !important;
                gap: 16px;
            }}

            .style-toggle {{
                top: 8px;
                right: 8px;
            }}

            .modern .card {{
                padding: 18px;
            }}

            .retro .card {{
                padding: 14px;
            }}

            .modern .card-header h2 {{
                font-size: 1em;
            }}

            .retro .card-header h2 {{
                font-size: 0.6em;
            }}
        }}
    </style>
</head>
<body class="modern">
    <div class="style-toggle">
        <label for="style-switch" id="label-retro">Retro</label>
        <div class="toggle-switch">
            <input type="checkbox" id="style-switch" checked>
            <span class="toggle-slider"></span>
        </div>
        <label for="style-switch" id="label-modern">Modern</label>
    </div>

    <div class="weather-bg">
        <div class="particle" style="width:80px;height:80px;background:rgba(255,255,255,0.1);top:10%;left:20%;animation-delay:0s;"></div>
        <div class="particle" style="width:120px;height:120px;background:rgba(255,255,255,0.08);top:50%;left:70%;animation-delay:2s;"></div>
        <div class="particle" style="width:60px;height:60px;background:rgba(255,255,255,0.12);top:30%;left:50%;animation-delay:4s;"></div>
        <div class="particle" style="width:100px;height:100px;background:rgba(255,255,255,0.06);top:70%;left:30%;animation-delay:1s;"></div>
        <div class="particle" style="width:90px;height:90px;background:rgba(255,255,255,0.1);top:80%;left:80%;animation-delay:3s;"></div>
    </div>

    <div class="container">
        <header>
            <h1>\U0001f3d8\ufe0f Temps a {LOCATION}</h1>
            <div class="weather-emoji">{emoji}</div>
            <p class="weather-desc">{desc}</p>
            <div class="temp-main">{temp}\u00b0C</div>
        </header>

        <div class="weather-summary">
            <div class="weather-detail">
                <span class="detail-icon">\U0001f321\ufe0f</span>
                <span>Sensaci\u00f3: {feels_like}\u00b0C</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">\U0001f4c8</span>
                <span>M\u00e0x: {temp_max}\u00b0C / M\u00edn: {temp_min}\u00b0C</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">\U0001f321\ufe0f</span>
                <span>Sensaci\u00f3 m\u00e0x: {feels_max}\u00b0C / m\u00edn: {feels_min}\u00b0C</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">\U0001f4a8</span>
                <span>Vent: {wind_speed} km/h</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">\u2601\ufe0f</span>
                <span>N\u00favols: {cloud_cover}%</span>
            </div>
            {rain_info}
        </div>

        <div class="cards-grid">
            {cards_html}
        </div>

        <footer>
            <p>Actualitzat: {update_time}</p>
            <p>Dades meteorol\u00f2giques proporcionades per <a href="https://open-meteo.com/" style="color:inherit;">Open-Meteo</a></p>
        </footer>
    </div>

    <script>
        (function() {{
            var toggle = document.getElementById('style-switch');
            var body = document.body;
            var saved = localStorage.getItem('temps-cabrils-style');
            if (saved === 'retro') {{
                body.className = 'retro';
                toggle.checked = false;
            }} else {{
                body.className = 'modern';
                toggle.checked = true;
            }}
            toggle.addEventListener('change', function() {{
                if (toggle.checked) {{
                    body.className = 'modern';
                    localStorage.setItem('temps-cabrils-style', 'modern');
                }} else {{
                    body.className = 'retro';
                    localStorage.setItem('temps-cabrils-style', 'retro');
                }}
            }});
        }})();
    </script>
</body>
</html>"""

    return html


def main():
    """Main entry point."""
    output_dir = os.environ.get("OUTPUT_DIR", "output")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Obtenint dades meteorològiques per a {LOCATION}...")
    weather_data = fetch_weather()
    print("Dades obtingudes correctament.")

    current = weather_data["current"]
    print(
        f"  Temperatura: {current['temperature_2m']}°C"
        f"  (sensació: {current['apparent_temperature']}°C)"
    )
    print(f"  Pluja: {current['rain']} mm")
    print(f"  Núvols: {current['cloud_cover']}%")
    print(f"  És de dia: {bool(current['is_day'])}")

    print("Generant pàgina HTML...")
    html = generate_html(weather_data)

    output_path = os.path.join(output_dir, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Pàgina generada: {output_path}")


if __name__ == "__main__":
    main()
