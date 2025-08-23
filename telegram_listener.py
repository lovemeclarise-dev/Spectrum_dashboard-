from telethon import TelegramClient, events
import config
import logging
from signal_parser import parse_signal_source_one, parse_signal_source_two
from termcolor import colored
import datetime
import asyncio

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def preprocess_and_validate_signal(signal_text):
    try:
        lines = signal_text.splitlines()
        signal = {}
        for line in lines:
            if "Expiration" in line:
                signal['expiration'] = line.split()[-1].replace('M', ' min')
            elif "Entry at" in line:
                signal['time'] = line.split()[-1]
            elif "BUY" in line or "SELL" in line:
                signal['entry_type'] = "CALL" if "BUY" in line else "PUT"
            elif "GBP" in line or "JPY" in line or "USD" in line:
                signal['pair'] = line.replace("", "").replace("", "").replace("", "").strip()
        return True, signal
    except Exception as e:
        print(f"Error during signal validation: {e}")
        return False, None

async def wait_until_time(time_str):
    time_format = "%H:%M"
    target_time = datetime.datetime.strptime(time_str, time_format).time()
    now = datetime.datetime.now()
    target_datetime = now.replace(hour=target_time.hour, minute=target_time.minute, second=0)
    if target_datetime < now:
        target_datetime += datetime.timedelta(days=1)
    wait_seconds = (target_datetime - now).total_seconds()
    await asyncio.sleep(wait_seconds)
    return True

class TelegramListener:
    def __init__(self, trade_executor):
        try:
            self.client = TelegramClient("session", config.TELEGRAM_API_ID, config.TELEGRAM_API_HASH)
            self.trade_executor = trade_executor
            logging.info("Telegram client initialized successfully!")
            print("Telegram client initialized successfully!")
        except Exception as e:
            logging.error(f"Error initializing Telegram client: {e}")
            print(f"Error initializing Telegram client: {e}")

    def start_listening(self):
        self.client.add_event_handler(self.handler_one, events.NewMessage(chats=int(config.TELEGRAM_CHANNEL_ONE)))
        self.client.add_event_handler(self.handler_two, events.NewMessage(chats=int(config.TELEGRAM_CHANNEL_TWO)))

    async def start(self):
        try:
            await self.client.start()
            self.start_listening()
            logging.info(f"Listening to channels {config.TELEGRAM_CHANNEL_ONE} and {config.TELEGRAM_CHANNEL_TWO}...")
            print(f"Listening to channels {config.TELEGRAM_CHANNEL_ONE} and {config.TELEGRAM_CHANNEL_TWO}...")
            logging.info("Telegram client started successfully!")
            print("Telegram client started successfully!")
            await self.client.run_until_disconnected()
        except Exception as e:
            logging.error(f"Error starting Telegram client: {e}")
            print(f"Error starting Telegram client: {e}")

    async def handler_one(self, event):
        try:
            logging.info("New message received from channel one!")
            print("New message received from channel one!")
            signal_text = event.raw_text
            valid, signal = await preprocess_and_validate_signal(signal_text)
            if valid:
                logging.info(f"Signal: {signal}")
                print(f"Signal: {signal}")
                duration = 300 if signal['expiration'] == '5 min' else 60
                action = signal["entry_type"].lower()
                amount = 1  # adjust amount as needed
                asset = signal["pair"]
                on_time = await wait_until_time(signal['time'])
                if on_time:
                    win = await self.trade_executor.trade(
                        duration=duration,
                        action=action,
                        amount=amount,
                        asset=asset
                    )
                    if not win:
                        print(colored("Entering First Martingale"), "yellow")
                        win = await self.trade_executor.trade(
                            duration=duration,
                            action=action,
                            amount=amount*2,
                            asset=asset
                        )
                        if not win:
                            print(colored("Entering Second Martingale"), "yellow")
                            win = await self.trade_executor.trade(
                                duration=duration,
                                action=action,
                                amount=amount*4,
                                asset=asset
                            )
            else:
                logging.error("Invalid signal format")
                print("Invalid signal format")
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            print(f"Error handling message: {e}")

    async def handler_two(self, event):
        try:
            logging.info("New message received from channel two!")
            print("New message
