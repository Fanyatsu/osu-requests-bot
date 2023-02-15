import logging
from osu_requests.twitch_bot import TwitchBot


LOG_FILENAME = "osu_requests.log"
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(message)s"
LOG_DATE_FORMAT = "%d.%m.%Y %H:%M:%S"

logging.basicConfig(
    format=LOG_FORMAT,
    datefmt=LOG_DATE_FORMAT,
    level=logging.INFO,
    handlers = [
        logging.StreamHandler(),
        logging.FileHandler(LOG_FILENAME)
    ]
)


if __name__ == '__main__':
    bot = TwitchBot()
    bot.run()
