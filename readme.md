## finds s&p stocks that are near their 52 week lows

### development stuff

install requirements
```bash
pip install yfinance discord
```

then run the script to find stocks that are near their 52 week lows
```bash
python 52lows.py
```

### run and post to discord

do this in linux. if you dont have linux, use wsl otherwise line endings will be stupid.

add a local `.env` file with your bot token and channel id
```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
ENVIRONMENT=local
```

and run the bot (which will run 52lows)
```bash
set -a
source .env
set +a
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

### docker environments behavior

- `ENVIRONMENT=local`: run `bot.py` once, post once, container exits (no cron).
- `ENVIRONMENT=dev`: start cron using `cronjob.dev`. (will only run test.py, not the full 52lows.py)
- `ENVIRONMENT=prod`: start cron using `cronjob.prod`.