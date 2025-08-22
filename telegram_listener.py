from telethon import TelegramClient, events
import config
import logging
from signal_parser import parse_signal_source_one, parse_signal_source_two

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

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

    async def start(self):
        try:
            await self.client.start()
            logging.info("Telegram client started successfully!")
            print("Telegram client started successfully!")
            await self.client.run_until_disconnected()
        except Exception as e:
            logging.error(f"Error starting Telegram client: {e}")
            print(f"Error starting Telegram client: {e}")

    @self.client.on(events.NewMessage(chats=int(config.TELEGRAM_CHANNEL_ONE)))
    async def handler_one(event):
        try:
            logging.info("New message received from channel one!")
            print("New message received from channel one!")
            signal = parse_signal_source_one(event.raw_text)
            if signal:
                logging.info(f"Currency Pair: {signal['asset']}")
                print(f"Currency Pair: {signal['asset']}")
                logging.info(f"Entry Time: {signal['entry']}")
                print(f"Entry Time: {signal['entry']}")
                logging.info(f"Direction: {signal['direction']}")
                print(f"Direction: {signal['direction']}")
                logging.info(f"Martingale Levels: {signal['martingale_levels']}")
                print(f"Martingale Levels: {signal['martingale_levels']}")
                await self.trade_executor.handle_signal(signal, source="one")
            else:
                logging.error("Message format not recognized")
                print("Message format not recognized")
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            print(f"Error handling message: {e}")

    @self.client.on(events.NewMessage(chats=int(config.TELEGRAM_CHANNEL_TWO)))
    async def handler_two(event):
        try:
            logging.info("New message received from channel two!")
            print("New message received from channel two!")
            signal = parse_signal_source_two(event.raw_text)
            if signal:
                logging.info(f"Currency Pair: {signal['asset']}")
                print(f"Currency Pair: {signal['asset']}")
                logging.info(f"Entry Time: {signal['entry']}")
                print(f"Entry Time: {signal['entry']}")
                logging.info(f"Direction: {signal['direction']}")
                print(f"Direction: {signal['direction']}")
                logging.info(f"Martingale Levels: {signal['martingale_levels']}")
                print(f"Martingale Levels: {signal['martingale_levels']}")
                await self.trade_executor.handle_signal(signal, source="two")
            else:
                logging.error("Message format not recognized")
                print("Message format not recognized")
        except Exception as e:
            logging.error(f"Error handling message: {e}")
            print(f"Error handling message: {e}")
