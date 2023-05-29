import re
import logging
from ossapi import OssapiAsync, Mod
from config import settings


logging.getLogger("ossapi").setLevel(logging.WARN)

api_v2 = OssapiAsync(settings.OSU_CLIENT_ID, settings.OSU_CLIENT_SECRET)

OSU_GAMEMODES_PREFIXES = {"mania": "🎹", "taiko": "🥁", "fruits": "🍏"}

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

OSU_MODS_PATTERN = re.compile(rf"(?<=\+)(?i)(?:{'|'.join(f'({mod.long_name()}|{mod.short_name()})' for mod in Mod.ORDER[:15])})+")


async def get_beatmap_objects(text):
    for link_type, pattern in OSU_BEATMAPS_PATTERNS.items():
        match = re.search(pattern, text)
        if not match:
            continue

        bm_id = match.groups()[-1]
        try:
            if "beatmap_" in link_type:
                beatmap = await api_v2.beatmap(bm_id)
                beatmapset = await api_v2.beatmapset(beatmap)
            elif "beatmapset_" in link_type:
                beatmapset = await api_v2.beatmapset(bm_id)
                beatmap = beatmapset.beatmaps[0]
            return beatmap, beatmapset
        except Exception as e:
            logging.error(e, exc_info=e, stack_info=True)

async def get_beatmap_data(beatmap, beatmapset, mods_object=None):
    url = f"https://osu.ppy.sh/b/{beatmap.id}"
    name = f"{beatmapset.artist} - {beatmapset.title} [{beatmap.version}]"

    if not mods_object:
        star_rating = beatmap.difficulty_rating
    else:
        beatmap_attributes = await api_v2.beatmap_attributes(beatmap.id, mods=mods_object)
        star_rating = beatmap_attributes.attributes.star_rating

    star_rating = round(star_rating, 2)
    status = beatmap.status.name.capitalize() if beatmap.status.value != -1 else beatmap.status.name
    mirror_url = f"https://api.chimu.moe/v1/download/{beatmapset.id}"

    return url, name, star_rating, status, mirror_url

async def get_user_object(text):
    match = re.search(OSU_USERS_PATTERN, text)
    if not match:
        return

    user_id = match.group(3)
    try:
        user = await api_v2.user(user_id)
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

def get_mods_object(text, mods_string=""):
    result = re.search(OSU_MODS_PATTERN, text)
    if not result:
        return

    for mod_name in result.groups():
        if not mod_name:
            continue

        mod_name = mod_name.upper()
        if len(mod_name) > 2:
            idx = [mod.long_name().upper() for mod in Mod.ORDER].index(mod_name)
            mod_name = Mod.ORDER[idx].short_name()

        mods_string += mod_name

    return Mod(mods_string)
