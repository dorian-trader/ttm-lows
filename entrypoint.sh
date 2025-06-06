#!/bin/bash

# load all env vars into cron's environment because apparently
# it runs in different environment than just running a script #wtf
printenv | grep -v "no_proxy" >> /etc/environment

if [[ "$ENVIRONMENT" == "dev" || "$ENVIRONMENT" == "local" ]]; then
  cp /etc/cron.d/cronjob.dev /etc/cron.d/active-cron
else
  cp /etc/cron.d/cronjob.prod /etc/cron.d/active-cron
fi

chmod 0644 /etc/cron.d/active-cron
crontab /etc/cron.d/active-cron

cron && tail -f /var/log/cron.log
