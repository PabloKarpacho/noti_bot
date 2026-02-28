FROM python:3.12-slim

WORKDIR /app

# cron + tzdata
RUN apt-get update \
  && apt-get install -y --no-install-recommends cron tzdata \
  && rm -rf /var/lib/apt/lists/*

ENV TZ=Europe/Rome

COPY pyproject.toml uv.lock ./

RUN pip install --no-cache-dir uv \
  && uv sync --frozen --no-dev \
  && rm -rf /root/.cache

# код — в /app/bot
COPY bot/ ./bot/

# cron jobs
COPY bot/scheduler/crontab /etc/cron.d/bot-cron
RUN chmod 0644 /etc/cron.d/bot-cron \
  && crontab /etc/cron.d/bot-cron \
  && touch /var/log/cron.log

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV PYTHONUNBUFFERED=1

CMD ["/entrypoint.sh"]