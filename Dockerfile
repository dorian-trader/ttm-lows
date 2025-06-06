FROM python:3.13.4-slim

WORKDIR /app

# Install cron + dependencies
RUN apt-get update && apt-get install -y cron && \
    pip install discord.py yfinance pandas beautifulsoup4 requests

COPY . .

# Copy both cronjob variants
COPY cronjob.dev /etc/cron.d/cronjob.dev
COPY cronjob.prod /etc/cron.d/cronjob.prod

# Entrypoint script to select cronjob
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN touch /var/log/cron.log

CMD ["/entrypoint.sh"]
