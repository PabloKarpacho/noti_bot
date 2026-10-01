## Start the application

```bash
uv run -m bot
```

## Database migrations (Alembic)

Use migration management script:

```bash
./scripts/manage_migrations.sh upgrade head
```

Useful commands:

```bash
./scripts/manage_migrations.sh current
./scripts/manage_migrations.sh history
./scripts/manage_migrations.sh deploy-upgrade
./scripts/manage_migrations.sh revision -m "your migration message"
```

For already deployed database without Alembic history (run once):

```bash
./scripts/manage_migrations.sh bootstrap-existing
```

CI/CD integration:

- Migration script runs automatically in container startup (`entrypoint.sh`) with `deploy-upgrade` mode before bot launch.
- On each deployment the service applies pending migrations before polling starts.

## Alice voice notes

The private Yandex Dialogs skill uses `https://216.57.104.246/alice/<secret>/<chat_id>/<thread_id>` as its Webhook URL for a forum topic, or omits `<thread_id>` to send to the general chat. The first empty request prompts for a note; later `SimpleUtterance.original_utterance` values are sent to the Telegram chat. A phrase supplied when launching the skill is sent immediately. The `ping` health check is never forwarded.

`ALICE_WEBHOOK_SECRET` is generated in the server's untracked `.env` on first deployment. Read it over SSH and keep the full URL private. For the forum topic `t.me/c/3865230303/1075`, use chat ID `-1003865230303` and thread ID `1075`.

The deploy workflow runs `scripts/configure_alice_https.sh` after updating the bot. It starts Nginx with a Let's Encrypt IP certificate and installs a systemd timer that checks renewal twice daily. Check it with `systemctl status noti-bot-alice-cert.timer`; run `systemctl start noti-bot-alice-cert.service` to check renewal manually. IP certificates last about six days and must be renewed automatically.
