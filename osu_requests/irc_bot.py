import asyncio
import logging
from irc.bot import SingleServerIRCBot, ExponentialBackoff
from irc.client import ServerConnection, Event


class IrcBot(SingleServerIRCBot):
    def __init__(self, username, server, port=6667, password=None):
        recon = ExponentialBackoff(min_interval=5, max_interval=30)
        SingleServerIRCBot.__init__(self, [(server, port, password)], username, username, recon=recon)
        self.messages_queue = asyncio.Queue()

    def on_welcome(self, c: ServerConnection, e: Event):
        logging.info(f"Connected to osu!IRC server as {self._nickname}")

    def send_message(self, target: str, text: str):
        target = target.replace(" ", "_")
        self.connection.privmsg(target, text)
        logging.info(f"In-Game message was successfully sent to {target}")
