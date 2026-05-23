from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from app.database.config import Base
from app.database.config import DATABASE_URL

# Import tất cả models
from app.database.config import *

config = context.config

config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=False,
    )

    with context.begin_transaction():
        context.run_migrations()


TRACKED_SCHEMAS = {"auth", "reference", "staging", "core", "log"}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if name == "alembic_version":
            return False
        schema = getattr(object, "schema", None) or "public"
        return schema in TRACKED_SCHEMAS
    return True


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True,
        include_object=include_object,
        version_table_schema="public",
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())