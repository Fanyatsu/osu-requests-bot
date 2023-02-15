import re
import logging
from ossapi import Ossapi
from config import settings


logging.getLogger("ossapi").setLevel(logging.WARN)

api_v2 = Ossapi(settings.OSU_CLIENT_ID, settings.OSU_CLIENT_SECRET)

OSU_GAMEMODES_PREFIXES = {
    "mania": "🎹", "taiko": "🥁", "fruits": "🍏"
}

OSU_BEATMAPS_PATTERNS = {
    "beatmap_official" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmapsets\/[0-9]+\#(osu|taiko|fruits|mania)\/([0-9]+)"),
    "beatmap_official_alternate" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmaps\/([0-9]+)"),
    "beatmap_old" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/b\/([0-9]+)"),
    "beatmap_old_alternate" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/p\/beatmap\?b=([0-9]+)"),
    "beatmapset_official" : re.compile(r"(?:https?:\/\/)?osu.ppy.sh\/beatmapsets\/([0-9]+)"),
    "beatmapset_old" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/s\/([0-9]+)"),
    "beatmapset_old_alternate" : re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/p\/beatmap\?s=([0-9]+)")
}

OSU_USERS_PATTERN = re.compile(r"(?:https?:\/\/)?(osu|old).ppy.sh\/(u|users)\/([^\s]+)")


def get_beatmap_objects(text):
    for link_type, pattern in OSU_BEATMAPS_PATTERNS.items():
        match = re.search(pattern, text)
        if not match:
            continue

        bm_id = match.groups()[-1]
        try:
            if "beatmap_" in link_type:
                beatmap = api_v2.beatmap(bm_id)
                beatmapset = api_v2.beatmapset(beatmap)
            elif "beatmapset_" in link_type:
                beatmapset = api_v2.beatmapset(bm_id)
                beatmap = beatmapset.beatmaps[0]
            return beatmap, beatmapset
        except Exception as e:
            logging.error(e, exc_info=e, stack_info=True)

def get_beatmap_data(beatmap, beatmapset):
    url = f"https://osu.ppy.sh/b/{beatmap.id}"
    name = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"
    star_rating = beatmap.difficulty_rating
    status = beatmap.status.name.capitalize() if beatmap.status.value != -1 else beatmap.status.name

    return url, name, star_rating, status

def get_user_object(text):
    match = re.search(OSU_USERS_PATTERN, text)
    if not match:
        return

    user_id = match.group(3)
    try:
        user = api_v2.user(user_id)
        return user
    except Exception as e:
        logging.error(e, exc_info=e, stack_info=True)

def get_user_data(user):
    gamemode = OSU_GAMEMODES_PREFIXES.get(user.playmode, "")
    name = user.username
    global_rank = user.statistics.global_rank
    country = user.country_code
    country_rank = user.statistics.country_rank
    pp = round(user.statistics.pp)

    return gamemode, name, global_rank, country, country_rank, pp
