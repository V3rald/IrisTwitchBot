import time

from bot import Bot

if __name__ == "__main__":
    while True:
        try:
            bot = Bot()
            bot.run()
        except Exception as e:
            print(f"Bot crashed: {e} — restarting in 10s")
            time.sleep(10)