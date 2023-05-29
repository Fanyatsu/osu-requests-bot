# osu! Requests Bot
Very simple osu! beatmap requests bot for Twitch streamers written in Python using ossapi, twitchio and irc libraries
> This project was inspired by **Ronnia** bot. Take a look: https://github.com/aticie/ronnia

## Screenshots
![Beatmap Link Handling](https://i.imgur.com/xDEWtr3.png) ![Profile Link Handling](https://i.imgur.com/c0Qck7S.png)
![In-Game osu! Message](https://i.imgur.com/K9E5B2b.png)

## Features
* Sending beatmap links from Twitch chat to In-Game osu! messages
* Responding to beatmap and profile links with general information
* Support for mods in beatmap requests (with star rate recalculation)
* Skipping requests handling from channel owner and users from ignore list
* Cooldown between In-Game osu! messages to avoid getting restricted

## Setup
> **Warning**
> **Python 3.7 or higher is required!**
1. Clone the repo - `git clone https://github.com/Fanyatsu/osu-requests-bot.git`
2. Open the directory where repo was cloned - `cd osu-requests-bot`
2. Install python dependencies - `pip install -r requirements.txt`
> **Note**
> Generally windows uses `py -m pip` and linux uses `python3 -m pip`
3. Fill the configuration file **config/settings.py** (please, read the comments)
4. Finally, run the bot using `run.py` file in the main directory

## Troubleshooting
**Q:** [Errno 13] Permission denied: osu_requests.log\
**A:** Grant your user write permissions to the log file

**Q:** Websocket connection was closed: None\
**A:** If you see this during startup, restart the bot

**Q:** Bot does not respond to links on Twitch chat\
**A:** Make the bot a channel moderator or disable follow/sub chat mode

**Q:** My requests are ignored when sent to my own Twitch chat\
**A:** Change "Skip channel owner requests" config option to False

## Support
Please let me know if you have any questions - www.fanyat.su
