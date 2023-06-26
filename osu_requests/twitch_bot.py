import asyncio
import logging
from threading import Thread
from typing import Union
from ossapi import Mod
from osu_requests.irc_bot import IrcBot
from osu_requests.osu_api import OsuAPIv2, BeatmapData, UserData
from osu_requests.osu_api import parse_mods_string, get_user_data, format_mods
from twitchio import Message, Channel, Chatter, PartialChatter
from twitchio.ext import commands, routines
from config import settings


class TwitchBot(commands.Bot):
    def __init__(self):
        self.channels = {key.lower(): value for key, value in settings.TTV_CHANNELS.items()}
        super().__init__(token=settings.TTV_ACCESS_TOKEN, prefix="!", initial_channels=[*self.channels])
        self.irc_bot = IrcBot(settings.OSU_IRC_USERNAME, settings.OSU_IRC_SERVER, password=settings.OSU_IRC_PASSWORD)
        self.irc_bot_thread = Thread(target=self.irc_bot.start)
        self.osu_api_v2 = OsuAPIv2(settings.OSU_CLIENT_ID, settings.OSU_CLIENT_SECRET)

    def run(self):
        self.irc_bot_thread.start()
        self.irc_messages_queue_worker.start()
        super().run()

    async def event_ready(self):
        logging.info(f"Connected to Twitch as {self.nick} (UID: {self.user_id})")

    async def event_message(self, message: Message):
        if not message.author:
            return

        await self.handle_request(message)
        await self.handle_profile(message)

    async def handle_request(self, message: Message):
        if message.author.name == message.channel.name and settings.SKIP_CHANNEL_OWNER_REQUESTS:
            return logging.debug(f"Skipping request handling from channel owner {message.author.name}")

        if message.author.name in settings.TTV_IGNORE_LIST:
            return logging.debug(f"Skipping request handling from ignored user {message.author.name}")

        results = await self.osu_api_v2.parse_beatmap_url(message.content)
        if not results:
            return

        mods = parse_mods_string(message.content)
        data = await self.osu_api_v2.get_beatmap_data(*results, mods)

        await self.send_request(data, mods, message.author, message.channel)

    async def handle_profile(self, message: Message):
        user = await self.osu_api_v2.parse_user_url(message.content)
        if not user:
            return

        data = get_user_data(user)
        await self.send_profile(data, message.channel)

    async def send_request(self, data: BeatmapData, mods: Mod, author: Union[Chatter, PartialChatter], channel: Channel):
        difficulty_params = f"{format_mods(mods)} ★ {data.star_rating:.2f}"

        twitch_message = f"[{data.status}] {data.name} {difficulty_params}"
        irc_message = (
            f"{author.name} » [{data.url} {data.name}] {difficulty_params} "
            f"⏰ {data.duration} ♫ {data.bpm:g} ({data.status}) [{data.mirror_url} mirror dl]"
        )

        await channel.send(twitch_message)
        self.irc_bot.messages_queue.put_nowait((self.channels[channel.name], irc_message))

    async def send_profile(self, data: UserData, channel: Channel):
        twitch_message = (
            f"{data.gamemode} {data.name} - #{data.global_rank or 0} "
            f"({data.country}: #{data.country_rank or 0}) {round(data.pp)}pp"
        )

        await channel.send(twitch_message)

    @routines.routine()
    async def irc_messages_queue_worker(self):
        target, text = await self.irc_bot.messages_queue.get()
        self.irc_bot.send_message(target, text)

        await asyncio.sleep(settings.PER_MESSAGE_COOLDOWN)

    @irc_messages_queue_worker.before_routine
    async def before_irc_messages_queue_worker(self):
        await self.wait_for_ready()
