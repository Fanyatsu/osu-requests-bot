import re
import datetime
import asyncio
import threading
import logging
import irc.bot
from twitchio.ext import commands
from twitchio import Message
from ossapi import OssapiV2, Beatmap, Beatmapset, User
from irc.client import Event, ServerConnection
from config import settings


LOG_FILENAME = "osurequests.log"
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
logging.getLogger("ossapi").setLevel(logging.WARN)

osu_api_v2 = OssapiV2(settings.OSU_CLIENT_ID, settings.OSU_CLIENT_SECRET)

OSU_BEATMAP_PATTERNS = {
    "beatmap_official" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmapsets\/[0-9]+\#(osu|taiko|fruits|mania)\/([0-9]+)"),
    "beatmap_old" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/b\/([0-9]+)"),
    "beatmap_alternate" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmaps\/([0-9]+)"),
    "beatmap_old_alternate" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/p\/beatmap\?b=([0-9]+)"),
    "beatmapset_official" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmapsets\/([0-9]+)"),
    "beatmapset_old" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/s\/([0-9]+)"),
    "beatmapset_old_alternate" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/p\/beatmap\?s=([0-9]+)"),
}

OSU_PROFILE_PATTERN = r"(?:https?:\/\/)?(osu|old).ppy.sh\/(u|users)\/([^\s]+)"


def parse_beatmap_objects_from_string(string: str):
    for link_type, pattern in OSU_BEATMAP_PATTERNS.items():
        match = re.search(pattern, string)
        if not match:
            continue

        bm_id = match.groups()[-1]
        try:
            if "beatmap_" in link_type:
                beatmap = osu_api_v2.beatmap(bm_id)
                beatmapset = osu_api_v2.beatmapset(beatmap)
            elif "beatmapset_" in link_type:
                beatmapset = osu_api_v2.beatmapset(bm_id)
                beatmap = beatmapset.beatmaps[0]
            return beatmap, beatmapset
        except Exception as e:
            logging.error(e, exc_info=e, stack_info=True)

def parse_profile_from_string(string: str):
    match = re.search(OSU_PROFILE_PATTERN, string)
    if not match:
        return

    user_id = match.group(3)
    try:
        user = osu_api_v2.user(user_id)
        return user
    except Exception as e:
        logging.error(e, exc_info=e, stack_info=True)


def get_beatmap_variables(beatmap: Beatmap, beatmapset: Beatmapset):
    version = beatmap.version
    status = beatmap.status.name.capitalize()
    rating = beatmap.difficulty_rating
    artist = beatmapset.artist
    title = beatmapset.title

    return version, status, rating, artist, title

def get_profile_variables(user: User):
    name = user.username
    global_rank = user.statistics.global_rank
    country = user.country_code
    country_rank = user.statistics.country_rank
    pp = round(user.statistics.pp)

    return name, global_rank, country, country_rank, pp


async def handle_request(self, message: Message):
    if settings.SKIP_CHANNEL_OWNER_REQUESTS and message.author.name == message.channel.name:
        return logging.debug(f"Skipping request handling from channel owner {message.author.name}")
    if message.author.name in settings.TTV_IGNORE_LIST:
        return logging.debug(f"Skipping request handling from ignored user {message.author.name}")

    beatmap_objects = parse_beatmap_objects_from_string(message.content)
    if beatmap_objects:
        beatmap, beatmapset = beatmap_objects
        version, status, rating, artist, title = get_beatmap_variables(beatmap, beatmapset)
        await message.channel.send(f"[{status}] {artist} - {title} [{version}] ★ {rating}")

        current_time = int(datetime.datetime.now().timestamp())
        next_request = self.last_request + settings.PER_MESSAGE_COOLDOWN
        if current_time < next_request:
            time_to_sleep = next_request - current_time
            logging.debug(f"Deferring In-Game request delivery for {time_to_sleep} seconds")
            await asyncio.sleep(time_to_sleep)
        self.last_request = current_time

        self.irc_bot.send_message(
            settings.TTV_CHANNELS[message.channel.name],
            f"Request from {message.author.name} » [https://osu.ppy.sh/b/{beatmap.id} {artist} - {title} [{version}]] ★ {rating} ({status})"
        )

async def handle_profile(message: Message):
    profile = parse_profile_from_string(message.content)
    if profile:
        name, global_rank, country, country_rank, pp = get_profile_variables(profile)
        await message.channel.send(f"{name} - #{global_rank} ({country}: #{country_rank}) {pp}pp")


class TwitchBot(commands.Bot):
    def __init__(self):
        super().__init__(token=settings.TTV_ACCESS_TOKEN, prefix="!", initial_channels=settings.TTV_CHANNELS)
        self.irc_bot = IrcBot(settings.OSU_IRC_USERNAME, settings.OSU_IRC_SERVER, password=settings.OSU_IRC_PASSWORD)
        self.irc_bot_thread = threading.Thread(target=self.irc_bot.start)
        self.last_request = 0

    def run(self):
        self.irc_bot_thread.start()
        super().run()

    async def event_ready(self):
        logging.info(f"Connected to Twitch as {self.nick} (UID: {self.user_id})")

    async def event_message(self, message):
        if not message.author:
            return

        await handle_request(self, message)
        await handle_profile(message)


class IrcBot(irc.bot.SingleServerIRCBot):
    def __init__(self, nickname, server, port=6667, password=None):
        reconnect_strategy = irc.bot.ExponentialBackoff(min_interval=5, max_interval=30)
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, password)], nickname, nickname, recon=reconnect_strategy)
        self.connection.set_rate_limit(1)

    def on_welcome(self, c: ServerConnection, e: Event):
        logging.info(f"Connected to osu!IRC server as {self._nickname}")

    def send_message(self, target: str, text: str):
        target = target.replace(" ", "_")
        self.connection.privmsg(target, text)
        logging.info(f"In-Game request was successfully sent to {target}")


if __name__ == '__main__':
    bot = TwitchBot()
    bot.run()
