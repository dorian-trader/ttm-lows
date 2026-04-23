import discord
import os
from io import BytesIO
import asyncio
import argparse
import sys
from pathlib import Path
import csv

BASE_DIR = Path(__file__).resolve().parent

def load_dotenv_file(path):
    """
    Load KEY=VALUE pairs from .env without overriding existing environment vars.
    This keeps Docker/runtime-provided env values authoritative.
    """
    env_path = Path(path)
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        os.environ.setdefault(key, value)

def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Set it in your shell or .env file."
        )
    return value

load_dotenv_file(BASE_DIR / ".env")

TOKEN = require_env("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(require_env("DISCORD_CHANNEL_ID"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

SCRIPT_MAP = {
    "local": "52lows.py",
    "dev": "test.py",
    "prod": "52lows.py"
}

class WeeklyClient(discord.Client):
    def __init__(self, script_args=None, **kwargs):
        super().__init__(**kwargs)
        self.script_args = script_args or []

    async def on_ready(self):
        channel = self.get_channel(CHANNEL_ID)
        result = await run_script_async(self.script_args)
        csv_text = extract_csv_text(result)
        total_rows = count_csv_data_rows(csv_text)
        preview_limit = 10
        preview = build_tsv_preview(csv_text, max_rows=preview_limit)
        shown_rows = min(preview_limit, total_rows)
        file = discord.File(
            fp=BytesIO(csv_text.encode("utf-8")),
            filename="52-week-lows.csv"
        )

        await channel.send(
            content=(
                f"Showing top {shown_rows} of {total_rows} tickers near 52-week lows.\n"
                "Full results are in the attached CSV.\n"
                f"```text\n{preview}\n```"
            ),
            file=file
        )

        await self.close()

def extract_csv_text(text):
    lines = text.splitlines()
    csv_start = None
    for idx, line in enumerate(lines):
        if line.startswith("Ticker,"):
            csv_start = idx
            break

    if csv_start is None:
        return "Error,Details\nNo CSV output detected,Check script output\n"

    csv_lines = [line for line in lines[csv_start:] if line.strip()]
    return "\n".join(csv_lines) + "\n"

def build_tsv_preview(csv_text, max_rows=10):
    rows = list(csv.reader(csv_text.splitlines()))
    if not rows:
        return "No rows available."

    header = rows[0]
    data_rows = rows[1:1 + max_rows]

    # Keep headers short and easy to scan in Discord code blocks.
    rename_map = {
        "Ticker": "Ticker",
        "Current Price": "Price",
        "52-Week Low": "Low52",
        "52-Week High": "High52",
        "Distance %": "Dist%",
    }
    pretty_header = [rename_map.get(col, col) for col in header]
    preview_rows = [pretty_header] + data_rows

    widths = [max(len(row[i]) for row in preview_rows) for i in range(len(pretty_header))]
    tsv_lines = []
    for row in preview_rows:
        padded = [row[i].ljust(widths[i]) for i in range(len(pretty_header))]
        tsv_lines.append("\t".join(padded))

    return "\n".join(tsv_lines)

def count_csv_data_rows(csv_text):
    rows = list(csv.reader(csv_text.splitlines()))
    if not rows:
        return 0
    return max(len(rows) - 1, 0)

async def run_script_async(script_args):
    script = SCRIPT_MAP.get(ENVIRONMENT, "52lows.py")
    if ENVIRONMENT == "local":
        script_path = str(BASE_DIR / script)
        cwd = str(BASE_DIR)
    else:
        script_path = f"/app/{script}"
        cwd = "/app"
    
    proc = await asyncio.create_subprocess_exec(
        sys.executable, script_path, *script_args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return (
            f"Script error (python: {sys.executable}):\n{stderr.decode()}"
        )
    return stdout.decode()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Run 52-week-low report bot and forward args to underlying report script."
    )
    known_args, script_args = parser.parse_known_args()
    return known_args, script_args

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

_, forwarded_script_args = parse_args()
client = WeeklyClient(script_args=forwarded_script_args, intents=intents)
client.run(TOKEN)
