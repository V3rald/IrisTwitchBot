import os
from dotenv import (
    load_dotenv,
)

load_dotenv()

TWITCH_TOKEN = os.getenv("TWITCH_TOKEN")
TWITCH_REFRESH_TOKEN = os.getenv("TWITCH_REFRESH_TOKEN")
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TAIWAN_WEATHER_KEY = os.getenv("TAIWAN_WEATHER_KEY")
SE_JWT_TOKEN = os.getenv("SE_JWT_TOKEN")
SONG_API_URL = os.getenv("SONG_API_URL")

HK_WEATHER_TEMP_RAIN = "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang=en"
HK_WEATHER_WIND = "https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind.csv"
TAIWAN_WEATHER_API = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0001-001"
SHANGHAI_WEATHER_API = "https://api.open-meteo.com/v1/cma?latitude=31.2304&longitude=121.4737&current_weather=true&hourly=relativehumidity_2m,precipitation,windgusts_10m"

COOLDOWN_SECONDS = 3
SE_CHANNEL_ID = "6054a697a2ce64a5a392a49c"
BOT_NICK = "Current_Song"
CHANNEL = "irissiri129"

IRL_TIMERS = ["IRL"]
NORMAL_TIMERS = [
    "Instagram",
    "Youtube",
    "Discord",
    "Sub perks",
    "Prime",
    "Goth Challenge",
    "Goth Challenge CH",
]

WIND_DIRECTIONS = [
    "North",
    "NorthEast",
    "East",
    "SouthEast",
    "South",
    "SouthWest",
    "West",
    "NorthWest",
]
