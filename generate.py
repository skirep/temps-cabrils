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
    person: 'dona', 'home', 'nen3', 'nen6'
    """
    # Adjust effective temperature based on person type
    if person == "dona":
        # Fredulica: feels 3 degrees colder
        effective = feels_like - 3
    elif person == "home":
        # Not cold-sensitive: use feels_like directly
        effective = feels_like
    elif person in ("nen3", "nen6"):
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
        elif person == "nen3":
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
        elif person == "nen3":
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
        elif person == "nen3":
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
        elif person == "nen3":
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
        elif person == "nen3":
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
        elif person == "nen3":
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
        if person in ("nen3", "nen6"):
            items.append("Botes d'aigua")
            items.append("Impermeable amb caputxa")
        elif person == "dona":
            items.append("Impermeable o jaqueta amb caputxa")
        else:
            items.append("Impermeable o jaqueta impermeble")

    # Sun protection
    if is_sunny and effective >= 20:
        items.append("Crema solar 🧴")
        if person in ("nen3", "nen6"):
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
        "nen3": ("👶", "Nen (3 anys)"),
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

    people = ["dona", "home", "nen6", "nen3"]
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
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: {bg_gradient};
            background-color: {bg_color};
            min-height: 100vh;
            color: {text_color};
            background-attachment: fixed;
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
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
        }}

        header {{
            text-align: center;
            padding: 30px 20px;
            color: {header_text_color};
        }}

        header h1 {{
            font-size: 2.2em;
            margin-bottom: 10px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }}

        .weather-emoji {{
            font-size: 4em;
            margin: 15px 0;
            filter: drop-shadow(0 4px 6px rgba(0,0,0,0.2));
        }}

        .weather-summary {{
            background: rgba(255,255,255,0.2);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0 30px;
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }}

        .weather-detail {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 1.1em;
            padding: 8px 16px;
            background: rgba(255,255,255,0.15);
            border-radius: 12px;
        }}

        .detail-icon {{
            font-size: 1.3em;
        }}

        .temp-main {{
            font-size: 3em;
            font-weight: bold;
            text-shadow: 0 2px 4px rgba(0,0,0,0.15);
        }}

        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}

        .card {{
            background: rgba(255,255,255,0.9);
            border-radius: 16px;
            padding: 25px;
            color: #2d3436;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }}

        .card:hover {{
            transform: translateY(-4px);
        }}

        .card-header {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
        }}

        .person-icon {{
            font-size: 2.2em;
        }}

        .card-header h2 {{
            font-size: 1.3em;
            color: #2d3436;
        }}

        .clothing-list {{
            list-style: none;
            padding: 0;
        }}

        .clothing-list li {{
            padding: 8px 12px;
            margin: 4px 0;
            background: #f8f9fa;
            border-radius: 8px;
            font-size: 0.95em;
            border-left: 3px solid #74b9ff;
        }}

        .clothing-list li:nth-child(even) {{
            border-left-color: #a29bfe;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            opacity: 0.8;
            font-size: 0.9em;
        }}

        @media (max-width: 600px) {{
            header h1 {{
                font-size: 1.5em;
            }}
            .temp-main {{
                font-size: 2em;
            }}
            .weather-summary {{
                flex-direction: column;
                align-items: center;
            }}
            .cards-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="weather-bg">
        <div class="particle" style="width:80px;height:80px;background:rgba(255,255,255,0.1);top:10%;left:20%;animation-delay:0s;"></div>
        <div class="particle" style="width:120px;height:120px;background:rgba(255,255,255,0.08);top:50%;left:70%;animation-delay:2s;"></div>
        <div class="particle" style="width:60px;height:60px;background:rgba(255,255,255,0.12);top:30%;left:50%;animation-delay:4s;"></div>
        <div class="particle" style="width:100px;height:100px;background:rgba(255,255,255,0.06);top:70%;left:30%;animation-delay:1s;"></div>
        <div class="particle" style="width:90px;height:90px;background:rgba(255,255,255,0.1);top:80%;left:80%;animation-delay:3s;"></div>
    </div>

    <div class="container">
        <header>
            <h1>🏘️ Temps a {LOCATION}</h1>
            <div class="weather-emoji">{emoji}</div>
            <p style="font-size:1.3em;margin-bottom:8px;">{desc}</p>
            <div class="temp-main">{temp}°C</div>
        </header>

        <div class="weather-summary">
            <div class="weather-detail">
                <span class="detail-icon">🌡️</span>
                <span>Sensació: {feels_like}°C</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">📈</span>
                <span>Màx: {temp_max}°C / Mín: {temp_min}°C</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">🌡️</span>
                <span>Sensació màx: {feels_max}°C / mín: {feels_min}°C</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">💨</span>
                <span>Vent: {wind_speed} km/h</span>
            </div>
            <div class="weather-detail">
                <span class="detail-icon">☁️</span>
                <span>Núvols: {cloud_cover}%</span>
            </div>
            {rain_info}
        </div>

        <div class="cards-grid">
            {cards_html}
        </div>

        <footer>
            <p>Actualitzat: {update_time}</p>
            <p>Dades meteorològiques proporcionades per <a href="https://open-meteo.com/" style="color:inherit;">Open-Meteo</a></p>
        </footer>
    </div>
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
