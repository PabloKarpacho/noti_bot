#!/usr/bin/env bash
set -euo pipefail

cd /root/noti_bot

docker run --rm --publish 80:80 \
  --volume /opt/noti-bot-certbot:/etc/letsencrypt \
  --volume /opt/noti-bot-certbot/lib:/var/lib/letsencrypt \
  certbot/certbot:latest renew --non-interactive

docker compose --profile alice exec -T alice_https nginx -s reload
