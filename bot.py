import discord
import os
from io import StringIO
import asyncio

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID"))
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")

SCRIPT_MAP = {
    "local": "52lows.py",
    "dev": "test.py",
    "prod": "52lows.py"
}

class WeeklyClient(discord.Client):
    async def on_ready(self):
        channel = self.get_channel(CHANNEL_ID)
        result = await run_script_async()

        summary = extract_summary(result)
        await channel.send(f"```\n{summary}\n```")

        buffer = StringIO(result)
        file = discord.File(fp=buffer, filename="weekly_52lows.txt")

        await channel.send("Stocks within 15% of 52-week lows:", file=file)

        await self.close()

def extract_summary(text):
    lines = text.splitlines()
    summary_lines = []
    total_length = 0
    for line in lines:
        if total_length + len(line) + 1 > 1900:
            break
        summary_lines.append(line)
        total_length += len(line) + 1  # account for newline

    # Trim to last "Distance" line
    for i in reversed(range(len(summary_lines))):
        if "Distance" in summary_lines[i]:
            return "\n".join(summary_lines[:i+1])
    return "\n".join(summary_lines[:10])  # fallback

async def run_script_async():
    script = SCRIPT_MAP.get(ENVIRONMENT, "52lows.py")

    if ENVIRONMENT == "local":
        script_path = script
    else:
        script_path = f"/app/{script}"
    
    proc = await asyncio.create_subprocess_exec(
        "python", script_path,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        return f"Script error:\n{stderr.decode()}"
    return stdout.decode()

intents = discord.Intents.default()
intents.guilds = True
intents.messages = True

client = WeeklyClient(intents=intents)
client.run(TOKEN)
