import re
import logging
from dataclasses import dataclass
from typing import Optional
from ossapi import OssapiAsync, Mod, Beatmap, Beatmapset, User
from ossapi.enums import RankStatus


logging.getLogger("ossapi").setLevel(logging.WARN)

OSU_GAMEMODES_PREFIXES = {"osu": "🟣", "mania": "🎹", "taiko": "🥁", "fruits": "🍏"}

OSU_BEATMAPS_PATTERNS = {
    "beatmap_official" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmapsets\/[0-9]+\#(osu|taiko|fruits|mania)\/([0-9]+)"),
    "beatmap_official_alternate" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmaps\/([0-9]+)"),
    "beatmap_old" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/b\/([0-9]+)"),
    "beatmap_old_alternate" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/p\/beatmap\?b=([0-9]+)"),
    "beatmapset_official" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmapsets\/([0-9]+)"),
    "beatmapset_old" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/s\/([0-9]+)"),
    "beatmapset_old_alternate" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/p\/beatmap\?s=([0-9]+)")
}

OSU_USERS_PATTERN = re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/(u|users)\/([^\/\s]+)")

OSU_MODS_PATTERN = re.compile(rf"(?<=\+)(?i)(?:{'|'.join(f'({mod.long_name()}|{mod.short_name()})' for mod in Mod.ORDER[:15])})+")


@dataclass
class BeatmapData:
    url: str
    name: str
    star_rating: float
    duration: str
    bpm: float
    status: str
    mirror_url: str

@dataclass
class UserData:
    gamemode: str
    name: str
    global_rank: int
    country: str
    country_rank: int
    pp: int


class OsuAPIv2(OssapiAsync):
    async def parse_beatmap_url(self, text: str) -> Optional[tuple[Beatmap, Beatmapset]]:
        for url_type, pattern in OSU_BEATMAPS_PATTERNS.items():
            match = re.search(pattern, text)
            if not match:
                continue

            result = match.groups()[-1]
            try:
                if "beatmap_" in url_type:
                    beatmap = await self.beatmap(result)
                    beatmapset = beatmap.beatmapset()
                elif "beatmapset_" in url_type:
                    beatmapset = await self.beatmapset(result)
                    beatmap = beatmapset.beatmaps[0]
                return beatmap, beatmapset
            except ValueError:
                return None
        return None

    async def parse_user_url(self, text: str) -> Optional[User]:
        match = re.search(OSU_USERS_PATTERN, text)
        if not match:
            return None

        result = match.group(3)
        try:
            user = await self.user(result)
            return user
        except ValueError:
            return None

    async def get_beatmap_star_rating(self, beatmap: Beatmap, mods: Optional[Mod]) -> float:
        if not mods:
            return beatmap.difficulty_rating

        beatmap_attributes = await self.beatmap_attributes(beatmap.id, mods=mods)
        return beatmap_attributes.attributes.star_rating

    async def get_beatmap_data(self, beatmap: Beatmap, beatmapset: Beatmapset, mods: Mod) -> BeatmapData:
        url = get_beatmap_url(beatmap.id)
        name = format_beatmap_name(beatmapset.artist, beatmapset.title, beatmap.version)
        star_rating = await self.get_beatmap_star_rating(beatmap, mods)
        duration = format_duration(beatmap.total_length, mods)
        bpm = format_bpm(beatmap.bpm, mods)
        status = format_beatmap_status(beatmap.status)
        mirror_url = get_mirror_url(beatmapset.id)

        return BeatmapData(url, name, star_rating, duration, bpm, status, mirror_url)


def get_user_data(user: User) -> UserData:
    gamemode = get_gamemode_prefix(user.playmode)
    name = user.username
    global_rank = user.statistics.global_rank
    country = user.country_code
    country_rank = user.statistics.country_rank
    pp = user.statistics.pp

    return UserData(gamemode, name, global_rank, country, country_rank, pp)

def parse_mods_string(text: str) -> Optional[Mod]:
    match = re.search(OSU_MODS_PATTERN, text)
    if not match:
        return

    mods = []
    for mod_name in match.groups():
        if not mod_name:
            continue

        mod_name = mod_name.upper()

        if len(mod_name) > 2:
            idx = [mod.long_name().upper() for mod in Mod.ORDER].index(mod_name)
            mod_name = Mod.ORDER[idx].short_name()

        mods.append(mod_name)

    return Mod(mods)

def get_beatmap_url(beatmap_id: int) -> str:
    return f"https://osu.ppy.sh/b/{beatmap_id}"

def format_beatmap_name(artist: str, title: str, version: str) -> str:
    return f"{artist} - {title} [{version}]"

def format_mods(mods: Mod) -> str:
    return f"+{mods.short_name()}" if mods else ""

def format_duration(seconds: int, mods: Mod) -> str:
    if mods:
        if Mod.DT in mods:
            seconds *= 0.67
        if Mod.HT in mods:
            seconds *= 1.33

    minutes, seconds = divmod(round(seconds), 60)
    hours, minutes = divmod(minutes, 60)

    if hours == 0:
        return f"{minutes:02d}:{seconds:02d}"

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_bpm(bpm: float, mods: Mod) -> float:
    if mods:
        if Mod.DT in mods:
            bpm *= 1.50
        if Mod.HT in mods:
            bpm *= 0.75

    return bpm

def format_beatmap_status(beatmap_status: RankStatus) -> str:
    if beatmap_status != RankStatus.WIP:
        return beatmap_status.name.capitalize()

    return beatmap_status.name

def get_mirror_url(beatmapset_id: int) -> str:
    return f"https://catboy.best/d/{beatmapset_id}"

def get_gamemode_prefix(gamemode: str) -> str:
    return OSU_GAMEMODES_PREFIXES.get(gamemode, "")
