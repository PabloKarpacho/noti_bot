#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

BASELINE_REVISION="20260315_01"

usage() {
  cat <<'EOF'
Usage:
  ./scripts/manage_migrations.sh upgrade [revision]
  ./scripts/manage_migrations.sh deploy-upgrade
  ./scripts/manage_migrations.sh downgrade [revision]
  ./scripts/manage_migrations.sh current
  ./scripts/manage_migrations.sh history
  ./scripts/manage_migrations.sh heads
  ./scripts/manage_migrations.sh stamp [revision]
  ./scripts/manage_migrations.sh revision -m "message"
  ./scripts/manage_migrations.sh bootstrap-existing

Commands:
  upgrade             Apply migrations (default revision: head)
  deploy-upgrade      Safe upgrade for CI/CD on both new and existing DB
  downgrade           Roll back migrations (default revision: -1)
  current             Show current revision
  history             Show migrations history
  heads               Show current heads
  stamp               Mark DB with a revision without executing migration SQL
  revision            Create a new autogenerate migration
  bootstrap-existing  Stamp existing DB to baseline and upgrade to head
EOF
}

command="${1:-upgrade}"

table_exists() {
  local table_name="$1"

  uv run python - "$table_name" <<'PY' >/dev/null
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from bot.config import settings


async def main() -> int:
    table = sys.argv[1]
    engine = create_async_engine(settings.db_postgres_url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text("SELECT to_regclass(:table_name)"),
                {"table_name": f"public.{table}"},
            )
            exists = result.scalar() is not None
            return 0 if exists else 1
    finally:
        await engine.dispose()


raise SystemExit(asyncio.run(main()))
PY
}

column_exists() {
  local table_name="$1"
  local column_name="$2"

  uv run python - "$table_name" "$column_name" <<'PY' >/dev/null
import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from bot.config import settings


async def main() -> int:
    table = sys.argv[1]
    column = sys.argv[2]
    engine = create_async_engine(settings.db_postgres_url)
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                text(
                    """
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND table_name = :table_name
                      AND column_name = :column_name
                    LIMIT 1
                    """
                ),
                {"table_name": table, "column_name": column},
            )
            exists = result.scalar() is not None
            return 0 if exists else 1
    finally:
        await engine.dispose()


raise SystemExit(asyncio.run(main()))
PY
}

deploy_upgrade() {
  if table_exists "alembic_version"; then
    uv run alembic upgrade head
    return
  fi

  if table_exists "users"; then
    if column_exists "notifications" "sticker_sent" && column_exists "notifications" "last_bot_message_id"; then
      uv run alembic stamp head
      return
    fi

    uv run alembic stamp "$BASELINE_REVISION"
    uv run alembic upgrade head
    return
  fi

  uv run alembic upgrade head
}

case "$command" in
  upgrade)
    target="${2:-head}"
    uv run alembic upgrade "$target"
    ;;
  deploy-upgrade)
    deploy_upgrade
    ;;
  downgrade)
    target="${2:--1}"
    uv run alembic downgrade "$target"
    ;;
  current)
    uv run alembic current
    ;;
  history)
    uv run alembic history --verbose
    ;;
  heads)
    uv run alembic heads
    ;;
  stamp)
    target="${2:-head}"
    uv run alembic stamp "$target"
    ;;
  revision)
    shift || true
    if [[ $# -eq 0 ]]; then
      echo "Error: revision command requires arguments, example: -m \"add column\"" >&2
      usage
      exit 1
    fi
    uv run alembic revision --autogenerate "$@"
    ;;
  bootstrap-existing)
    uv run alembic stamp "$BASELINE_REVISION"
    uv run alembic upgrade head
    ;;
  *)
    usage
    exit 1
    ;;
esac
