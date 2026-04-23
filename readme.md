## 52-week lows/highs Discord bot

Small runbook for running reports and debugging different execution modes.

## Quick setup

Install dependencies:

```bash
pip install yfinance discord.py pandas beautifulsoup4 requests
```

Create `.env` (used by local and Docker runs):

```bash
DISCORD_BOT_TOKEN=your_discord_bot_token
DISCORD_CHANNEL_ID=your_discord_channel_id
ENVIRONMENT=local
```

Optional:

- `REPORT_TYPE=lows|highs` (used when `--report` is not passed)

## Run report scripts directly (no Discord)

```bash
python 52lows.py
python 52highs.py
```

## Run bot locally (one-shot, post once)

Low report:

```bash
python bot.py --report lows
```

High report:

```bash
python bot.py --report highs
```

If you omit `--report`, bot uses `REPORT_TYPE` env var (default: `lows`).

## Docker

Build:

```bash
docker build -t 52lows .
```

### Docker one-shot (best for debugging a single job)

Highs only:

```bash
docker run --rm --env-file .env -e ENVIRONMENT=local -e REPORT_TYPE=highs 52lows
```

Lows only:

```bash
docker run --rm --env-file .env -e ENVIRONMENT=local -e REPORT_TYPE=lows 52lows
```

### Docker cron modes

- `ENVIRONMENT=dev`: runs `cronjob.dev` (uses `test.py`, debug payload only)
- `ENVIRONMENT=prod`: runs `cronjob.prod` (real schedules)

Current prod cron schedule:

- 52-week lows: Mon-Fri `13:30 UTC`
- 52-week highs: Mon-Fri `16:00 America/New_York`