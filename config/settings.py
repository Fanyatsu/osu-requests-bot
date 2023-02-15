# Twitch Chat OAuth Token of your Twitch bot account
# Can be generated here: https://twitchapps.com/tmi/
TTV_ACCESS_TOKEN = ""

# Twitch usernames to globally ignore requests from
# Example: ["username1", "username2", "username3"]
TTV_IGNORE_LIST = []

# Twitch channel name : osu! username
# Example: {"shigetora" : "chocomint"}
TTV_CHANNELS = {}

# Username and IRC password of your osu! bot account
# Located at: https://osu.ppy.sh/p/irc
OSU_IRC_USERNAME = ""
OSU_IRC_PASSWORD = ""
OSU_IRC_SERVER = "irc.ppy.sh"

# Client ID and Client Secret of your osu! OAuth application
# Create your own here: https://osu.ppy.sh/home/account/edit
OSU_CLIENT_ID = ""
OSU_CLIENT_SECRET = ""

# Whether to skip (ignore) requests from Twitch channel owner
# Skip - True | Don't skip - False
SKIP_CHANNEL_OWNER_REQUESTS = False

# Cooldown (in seconds) between In-Game osu! messages
# Personal accounts can send 10 messages every 5 seconds
# Bot accounts can send 300 messages every 60 seconds
# Source: https://osu.ppy.sh/wiki/en/Bot_account
PER_MESSAGE_COOLDOWN = 2.5
