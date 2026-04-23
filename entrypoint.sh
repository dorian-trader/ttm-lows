#!/bin/bash

set -euo pipefail

# load all env vars into cron's environment because apparently
# it runs in different environment than just running a script #wtf
printenv | grep -v "no_proxy" >> /etc/environment

# Local Docker runs should execute once and exit, without cron.
if [[ "${ENVIRONMENT:-dev}" == "local" ]]; then
  echo "ENVIRONMENT=local -> running bot once and exiting"
  python /app/bot.py
  exit 0
fi

if [[ "${ENVIRONMENT:-dev}" == "dev" ]]; then
  cp /etc/cron.d/cronjob.dev /etc/cron.d/active-cron
else
  cp /etc/cron.d/cronjob.prod /etc/cron.d/active-cron
fi

chmod 0644 /etc/cron.d/active-cron
crontab /etc/cron.d/active-cron

echo "Starting cron for ENVIRONMENT=${ENVIRONMENT:-dev}"
cron
tail -f /var/log/cron.log
