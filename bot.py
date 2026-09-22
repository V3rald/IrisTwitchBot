import sys
import time
import requests
import aiohttp
from typing import Optional
from twitchio.ext import commands

from config import (
    TWITCH_CLIENT_ID, CHANNEL, SE_JWT_TOKEN, SE_CHANNEL_ID,
    SONG_API_URL, COOLDOWN_SECONDS, IRL_TIMERS, NORMAL_TIMERS
)
from token_manager import TwitchBotTokenManager, TwitchAppTokenManager
from weather import WEATHER_FUNCTIONS


class Bot(commands.Bot):

    def __init__(self):
        self.app_tm = TwitchAppTokenManager()
        self.bot_tm = TwitchBotTokenManager()
        self.irl_mode = False
        self.weather_country = "hk"
        self._last_used: dict[str, float] = {}

        super().__init__(token=self.bot_tm.get_token(), prefix="!", initial_channels=[CHANNEL])

    # ===== LIFECYCLE =====

    async def event_ready(self):
        print(f"Logged in as {self.nick} | Channel: {CHANNEL}")
        self._connection._token = self.bot_tm.get_token()

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            return

    async def event_error(self, error: Exception, data=None):
        import traceback
        print(f"Error: {error}")
        traceback.print_exc()

    # ===== HELPERS =====

    def _on_cooldown(self, key: str) -> bool:
        now = time.time()
        if now - self._last_used.get(key, 0) < COOLDOWN_SECONDS:
            return True
        self._last_used[key] = now
        return False

    def is_live(self) -> bool:
        r = requests.get(
            "https://api.twitch.tv/helix/streams",
            params={"user_login": CHANNEL},
            headers={
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {self.app_tm.get_token()}",
            },
            timeout=5,
        )
        return bool(r.json().get("data"))

    async def _set_timers(self, session: aiohttp.ClientSession, timer_map: dict, names: list, enabled: bool):
        for name in names:
            timer = timer_map.get(name)
            if not timer:
                print(f"Timer not found: {name}")
                continue
            async with session.put(
                f"https://api.streamelements.com/kappa/v2/bot/timers/{SE_CHANNEL_ID}/{timer['_id']}",
                json={**timer, "enabled": enabled},
            ) as r:
                if r.status not in (200, 201):
                    print(f"Failed to update timer '{name}': {r.status}")

    # ===== COMMANDS =====

    @commands.command(name="help")
    async def help(self, ctx):
        await ctx.send("!weather | !song | !irl <on/off> | !setweather <hk/tw/sh>")

    @commands.command(name="song")
    async def song(self, ctx):
        if not self.is_live():
            await ctx.send("Streamer is offline")
            return

        if self._on_cooldown("song"):
            return

        try:
            r = requests.get(SONG_API_URL, timeout=5)
            r.raise_for_status()
            data = r.json()
            title = data.get("title", "Unknown")
            url = data.get("url", "")

            if title == "Nothing playing":
                await ctx.send("Nothing is currently playing right now.")
            elif url:
                await ctx.send(f"🎵 {title} - {url}")
            else:
                await ctx.send(f"🎵 {title}")

        except Exception as e:
            print(f"Error fetching song: {e}")
            await ctx.send("Failed to fetch current song.")

    @commands.command(name="weather")
    async def weather(self, ctx):
        if self._on_cooldown("weather"):
            return

        get_weather = WEATHER_FUNCTIONS.get(self.weather_country, WEATHER_FUNCTIONS["hk"])
        w = await get_weather()

        rain = f"{w['rainfall']} mm 🌧️" if w["is_raining"] else "☀️"
        wind = f"Wind is blowing from the {w['wind_direction']} at {w['wind_speed']} km/h (Maximum Gust is {w['wind_gust']} km/h)"
        typhoon = f"| Typhoon: {w['typhoon']}" if w["typhoon"] else ""

        await ctx.send(
            f"{w['location']}: {w['temperature']} C | {rain} | {wind} | Humidity: {w['humidity']}% {typhoon}"
        )

    @commands.command(name="setweather")
    async def setweather(self, ctx, country: Optional[str] = None):
        if not ctx.author.is_mod or country not in WEATHER_FUNCTIONS:
            return

        self.weather_country = country
        names = {"hk": "Hong Kong", "tw": "Taiwan, Taipei", "sh": "Shanghai"}
        await ctx.send(f"Weather command changed to {names[country]}")

    @commands.command(name="irl")
    async def irl(self, ctx, mode: Optional[str] = None):
        if not ctx.author.is_mod:
            return

        if mode in ("on", "enable"):
            self.irl_mode = True
        elif mode in ("off", "disable"):
            self.irl_mode = False
        else:
            self.irl_mode = not self.irl_mode

        headers = {
            "Authorization": f"Bearer {SE_JWT_TOKEN}",
            "Content-Type": "application/json",
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                f"https://api.streamelements.com/kappa/v2/bot/timers/{SE_CHANNEL_ID}"
            ) as r:
                timer_map = {t["name"]: t for t in await r.json()}

            if self.irl_mode:
                await self._set_timers(session, timer_map, IRL_TIMERS, enabled=True)
                await self._set_timers(session, timer_map, NORMAL_TIMERS, enabled=False)
                await ctx.send("Stream mode set to: IRL")
            else:
                await self._set_timers(session, timer_map, IRL_TIMERS, enabled=False)
                await self._set_timers(session, timer_map, NORMAL_TIMERS, enabled=True)
                await ctx.send("Stream mode set to: Desktop")