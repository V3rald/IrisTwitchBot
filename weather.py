import csv
import aiohttp
from types import SimpleNamespace
from config import (
    HK_WEATHER_TEMP_RAIN, HK_WEATHER_WIND,
    TAIWAN_WEATHER_API, TAIWAN_WEATHER_KEY,
    SHANGHAI_WEATHER_API, WIND_DIRECTIONS
)


def _degrees_to_direction(degrees: float) -> str:
    return WIND_DIRECTIONS[round(degrees / 45) % 8]


def _dict_to_object(data):
    if isinstance(data, dict):
        return SimpleNamespace(**{k: _dict_to_object(v) for k, v in data.items()})
    if isinstance(data, list):
        return [_dict_to_object(x) for x in data]
    return data


async def get_hk_weather() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(HK_WEATHER_WIND) as r:
            text = await r.text()
        async with session.get(HK_WEATHER_TEMP_RAIN) as r:
            weather = _dict_to_object(await r.json())

    wind = next(
        row for row in csv.DictReader(text.splitlines())
        if row["Automatic Weather Station"] == "Tuen Mun"
    )
    rain = next(x for x in weather.rainfall.data if x.place == "Tuen Mun")
    temp = next(x for x in weather.temperature.data if x.place == "Tuen Mun")

    return {
        "location": "Hong Kong",
        "temperature": temp.value,
        "humidity": weather.humidity.data[0].value,
        "rainfall": rain.max,
        "is_raining": rain.main == "TRUE",
        "wind_speed": int(wind["10-Minute Mean Speed(km/hour)"]),
        "wind_gust": int(wind["10-Minute Maximum Gust(km/hour)"]),
        "wind_direction": wind["10-Minute Mean Wind Direction(Compass points)"],
        "typhoon": weather.tcmessage,
    }


async def get_taipei_weather() -> dict:
    async with aiohttp.ClientSession(headers={"Authorization": TAIWAN_WEATHER_KEY}) as session:
        async with session.get(TAIWAN_WEATHER_API, params={"StationId": "466920"}) as r:
            data = await r.json()

    el = data["records"]["Station"][0]["WeatherElement"]
    peak_gust = el["GustInfo"]["PeakGustSpeed"]

    return {
        "location": "Taiwan, Taipei",
        "temperature": float(el["AirTemperature"]),
        "humidity": int(el["RelativeHumidity"]),
        "rainfall": float(el["Now"]["Precipitation"]),
        "is_raining": any(c in el["Weather"] for c in ["雨", "大雨", "雷雨"]),
        "wind_speed": float(el["WindSpeed"]),
        "wind_gust": "Unknown" if peak_gust == "-99" else float(peak_gust),
        "wind_direction": _degrees_to_direction(float(el["WindDirection"])),
        "typhoon": "",
    }


async def get_shanghai_weather() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(SHANGHAI_WEATHER_API) as r:
            data = await r.json()

    current = data["current_weather"]
    hour_index = data["hourly"]["time"].index(current["time"])

    return {
        "location": "Shanghai",
        "temperature": current["temperature"],
        "humidity": data["hourly"]["relativehumidity_2m"][hour_index],
        "rainfall": data["hourly"]["precipitation"][hour_index],
        "is_raining": data["hourly"]["precipitation"][hour_index] > 0,
        "wind_speed": current["windspeed"],
        "wind_gust": data["hourly"]["windgusts_10m"][hour_index],
        "wind_direction": _degrees_to_direction(current["winddirection"]),
        "typhoon": "",
    }


WEATHER_FUNCTIONS = {
    "hk": get_hk_weather,
    "tw": get_taipei_weather,
    "sh": get_shanghai_weather,
}