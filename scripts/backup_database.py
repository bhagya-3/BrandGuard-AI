"""Create a consistent SQLite or PostgreSQL database backup."""

import argparse
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy.engine import make_url

from app.core.config import settings
from app.core.database import engine


def parse_args():
    parser = argparse.ArgumentParser(description="Back up the configured BrandGuard database.")
    parser.add_argument("--output", type=Path, help="Destination file; defaults to ./backups with a timestamp.")
    parser.add_argument("--overwrite", action="store_true", help="Allow replacing an existing backup file.")
    return parser.parse_args()


def default_output(database_type):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    extension = "sqlite3" if database_type == "sqlite" else "dump"
    return Path("backups") / f"brandguard-{timestamp}.{extension}"


def backup_sqlite(destination):
    url = make_url(settings.DATABASE_URL)
    database_path = url.database
    if not database_path or database_path == ":memory:":
        raise ValueError("A file-backed SQLite database is required for backups.")

    source_path = Path(database_path)
    if not source_path.is_absolute():
        source_path = Path.cwd() / source_path
    if not source_path.exists():
        raise FileNotFoundError(f"SQLite database does not exist: {source_path}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with engine.connect() as connection:
        raw_connection = connection.connection
        source = getattr(raw_connection, "driver_connection", raw_connection)
        target = sqlite3.connect(str(destination))
        try:
            source.backup(target)
            result = target.execute("PRAGMA quick_check").fetchone()
            if not result or result[0] != "ok":
                raise RuntimeError("SQLite backup integrity check failed.")
        finally:
            target.close()


def backup_postgres(destination):
    executable = shutil.which("pg_dump")
    if not executable:
        raise RuntimeError("pg_dump was not found. Install PostgreSQL client tools to back up PostgreSQL.")

    url = make_url(settings.DATABASE_URL)
    if not url.database:
        raise ValueError("DATABASE_URL must include a PostgreSQL database name.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    environment = os.environ.copy()
    if url.password:
        environment["PGPASSWORD"] = url.password
    if url.query.get("sslmode"):
        environment["PGSSLMODE"] = str(url.query["sslmode"])

    command = [
        executable,
        "--format=custom",
        f"--file={destination}",
        f"--dbname={url.database}",
    ]
    if url.host:
        command.append(f"--host={url.host}")
    if url.port:
        command.append(f"--port={url.port}")
    if url.username:
        command.append(f"--username={url.username}")

    result = subprocess.run(
        command,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        message = result.stderr.strip() or "pg_dump failed."
        raise RuntimeError(message)


def main():
    args = parse_args()
    database_type = engine.dialect.name
    if database_type not in {"sqlite", "postgresql"}:
        print(f"Backups are not implemented for database type: {database_type}", file=sys.stderr)
        return 2

    destination = args.output or default_output(database_type)
    if destination.exists() and not args.overwrite:
        print(f"Backup already exists: {destination}. Pass --overwrite to replace it.", file=sys.stderr)
        return 2

    try:
        if database_type == "sqlite":
            backup_sqlite(destination)
        else:
            backup_postgres(destination)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Database backup failed: {error}", file=sys.stderr)
        return 1
    finally:
        engine.dispose()

    print(f"Database backup created: {destination.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())