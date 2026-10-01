#!/usr/bin/env bash
set -euo pipefail

cd /root/noti_bot

if ! grep -q '^ALICE_WEBHOOK_SECRET=.' .env; then
  printf '\nALICE_WEBHOOK_SECRET=%s\n' "$(openssl rand -hex 32)" >> .env
  docker compose up -d --force-recreate bot
fi

if [[ ! -f /opt/noti-bot-certbot/live/216.57.104.246/fullchain.pem ]]; then
  mkdir -p /opt/noti-bot-certbot/lib
  docker run --rm --publish 80:80 \
    --volume /opt/noti-bot-certbot:/etc/letsencrypt \
    --volume /opt/noti-bot-certbot/lib:/var/lib/letsencrypt \
    certbot/certbot:latest certonly --standalone --non-interactive \
    --agree-tos --register-unsafely-without-email \
    --preferred-profile shortlived --ip-address 216.57.104.246
fi

docker compose --profile alice up -d alice_https
install -m 0644 deploy/noti-bot-alice-cert.service /etc/systemd/system/
install -m 0644 deploy/noti-bot-alice-cert.timer /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now noti-bot-alice-cert.timer
