# Twitch Chat OAuth Token of your bot's account
# Can be generated here: https://twitchapps.com/tmi/
TTV_ACCESS_TOKEN = ""

# Twitch usernames to globally ignore requests from
# ["username1", "username2", "username3"]
TTV_IGNORE_LIST = []

# Twitch_username : osu!_username
# "shigetora" : "chocomint",
# "mrekkosu" : "mrekk",
TTV_CHANNELS = {
    
}

# Your osu! bot's account username and IRC password
# Located at: https://osu.ppy.sh/p/irc
OSU_IRC_USERNAME = ""
OSU_IRC_PASSWORD = ""
OSU_IRC_SERVER = "irc.ppy.sh"

# osu! OAuth application's Client ID and Client Secret
# Create one here: https://osu.ppy.sh/home/account/edit
OSU_CLIENT_ID = ""
OSU_CLIENT_SECRET = ""

# Whether to skip (ignore) requests from channel owner
# Skip - True | Don't skip - False
SKIP_CHANNEL_OWNER_REQUESTS = True

# Cooldown (in seconds) between In-Game osu! messages
# Personal accounts can send 10 messages every 5 seconds
# Bot accounts can send 300 messages every 60 seconds
# Source: https://osu.ppy.sh/wiki/en/Bot_account
PER_MESSAGE_COOLDOWN = 5
