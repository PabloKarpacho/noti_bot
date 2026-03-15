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