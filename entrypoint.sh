#!/bin/sh
set -e

# сохраняем текущее окружение контейнера в файл для cron
printenv | sed 's/^\([^=]*\)=\(.*\)$/export \1="\2"/' > /etc/cron.env

cron
tail -F /var/log/cron.log &

# запускаем бота (это главный процесс)
exec uv run -m bot