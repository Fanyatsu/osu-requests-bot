# osu! Requests Bot
Very simple Twitch --> osu! beatmap requests bot written in Python using ossapi, twitchio and irc libraries
> This project was inspired by **Ronnia** bot. Take a look: https://github.com/aticie/ronnia

## Screenshots
![Beatmap Link Handling](https://i.imgur.com/xDEWtr3.png) ![Profile Link Handling](https://i.imgur.com/c0Qck7S.png)
![In-Game osu! Message](https://i.imgur.com/K9E5B2b.png)

## Features
* Sending beatmap links from Twitch chat to osu! In-Game messages
* Responding to beatmap and profile links with basic information
* Skipping requests handling from channel owner and users from ignore list
* Cooldown between In-Game osu! messages to avoid getting restricted

## Setup
1. Make sure you have **Python 3.6** or newer version installed
2. Clone the repo - `git clone https://github.com/Fanyatsu/osu-requests-bot.git`
3. Change current working directory - `cd osu-requests-bot`
4. Install python dependencies - `pip install -r requirements.txt`
5. Fill the configuration file **config/settings.py** (comments will help you)
6. Finally, run the bot - `python main.py`

## Troubleshooting
⁉️ **OSError: [Errno 13] Permission denied: osurequests.log**  
🟢 Grant your user write permissions to the log file

⁉️ **In-Game messages delivery is noticeably delayed**  
🟢 Can be bad connection or Bancho is slow at the moment

## Support
Please let me know if you have any questions - www.fanyat.su
