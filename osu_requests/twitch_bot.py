import threading
import asyncio
import logging
from twitchio.ext import commands, routines
from osu_requests.irc_bot import IrcBot
from osu_requests import osu_api
from config import settings


class TwitchBot(commands.Bot):
    def __init__(self):
        self.channels = {key.lower(): value for key, value in settings.TTV_CHANNELS.items()}
        super().__init__(token=settings.TTV_ACCESS_TOKEN, prefix="!", initial_channels=[*self.channels])
        self.irc_bot = IrcBot(settings.OSU_IRC_USERNAME, settings.OSU_IRC_SERVER, password=settings.OSU_IRC_PASSWORD)
        self.irc_bot_thread = threading.Thread(target=self.irc_bot.start)
        self.irc_messages_queue = asyncio.Queue()

    def run(self):
        self.irc_bot_thread.start()
        self.irc_messages_queue_worker.start()
        super().run()

    async def event_ready(self):
        logging.info(f"Connected to Twitch as {self.nick} (UID: {self.user_id})")

    async def event_message(self, message):
        if not message.author:
            return

        await self.handle_request(message)
        await self.handle_profile(message)

    async def handle_request(self, message):
        if message.author.name == message.channel.name and settings.SKIP_CHANNEL_OWNER_REQUESTS:
            return logging.debug(f"Skipping request handling from channel owner {message.author.name}")

        if message.author.name in settings.TTV_IGNORE_LIST:
            return logging.debug(f"Skipping request handling from ignored user {message.author.name}")

        beatmap_objects = await osu_api.get_beatmap_objects(message.content)
        if not beatmap_objects:
            return

        mods_object = osu_api.get_mods_object(message.content)
        mods = f"+{mods_object.short_name()}" if mods_object else ""

        url, name, star_rating, status = await osu_api.get_beatmap_data(*beatmap_objects, mods_object)

        await message.channel.send(f"[{status}] {name} {mods} ★ {star_rating}")

        self.irc_messages_queue.put_nowait(
            (
                self.channels[message.channel.name],
                f"Request from {message.author.name} » [{url} {name}] {mods} ★ {star_rating} ({status})"
            )
        )

    async def handle_profile(self, message):
        user = await osu_api.get_user_object(message.content)
        if not user:
            return

        gamemode, name, global_rank, country, country_rank, pp = osu_api.get_user_data(user)
        await message.channel.send(f"{gamemode} {name} - #{global_rank} ({country}: #{country_rank}) {pp}pp")

    @routines.routine()
    async def irc_messages_queue_worker(self):
        target, text = await self.irc_messages_queue.get()
        self.irc_bot.send_message(target, text)

        await asyncio.sleep(settings.PER_MESSAGE_COOLDOWN)

    @irc_messages_queue_worker.before_routine
    async def before_irc_messages_queue_worker(self):
        await self.wait_for_ready()
