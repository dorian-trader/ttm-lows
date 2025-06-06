## finds s&p stocks that are near their 52 week lows

do this in linux. if you dont have linux, use wsl otherwise line endings will be stupid.

install requirements
```bash
pip install yfinance discord
```

then run the script to find stocks that are near their 52 week lows
```bash
python 52lows.py
```

if you have a discord bot, add a local .env file with your bot token and channel id
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
ENVIRONMENT=local
```

and run the bot (which will run 52lows)
```bash
python bot.py
```

## docker stuff
_note: this needs valid .env file to run_

build the docker image
```bash
docker build -t 52lows .
```

then run the docker container
```bash 
docker run --env-file .env 52lows
```