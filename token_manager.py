import time
import requests
from config import TWITCH_CLIENT_ID, TWITCH_CLIENT_SECRET, TWITCH_TOKEN, TWITCH_REFRESH_TOKEN


class TwitchBotTokenManager:
    """Manages the bot user's OAuth token (refresh token flow)."""

    def __init__(self):
        self.client_id = TWITCH_CLIENT_ID
        self.client_secret = TWITCH_CLIENT_SECRET
        self.token = TWITCH_TOKEN
        self.refresh_token = TWITCH_REFRESH_TOKEN
        self.expires_at = 0

    def get_token(self) -> str:
        if not self.token or time.time() >= self.expires_at:
            self._refresh()
        return self.token

    def _refresh(self):
        r = requests.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": self.refresh_token,
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        self.token = data["access_token"]
        self.refresh_token = data.get("refresh_token", self.refresh_token)
        self.expires_at = time.time() + data["expires_in"] - 60
        print("Bot token refreshed.")


class TwitchAppTokenManager:
    """Manages the app's client credentials token (for API calls like is_live)."""

    def __init__(self):
        self.client_id = TWITCH_CLIENT_ID
        self.client_secret = TWITCH_CLIENT_SECRET
        self.token = None
        self.expires_at = 0

    def get_token(self) -> str:
        if not self.token or time.time() >= self.expires_at:
            self._refresh()
        return self.token

    def _refresh(self):
        r = requests.post(
            "https://id.twitch.tv/oauth2/token",
            data={
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "grant_type": "client_credentials",
            },
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()

        self.token = data["access_token"]
        self.expires_at = time.time() + data["expires_in"] - 60