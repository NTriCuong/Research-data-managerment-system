import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool, text
from alembic import context

load_dotenv()


# ============================================================
#  Import Base từ config.py
#
#  config.py đã import toàn bộ model ở trên.
#  Chỉ cần import Base ở đây là đủ — Base.metadata
#  đã chứa thông tin của tất cả table/schema.
# ============================================================

from app.database.config import Base


# ============================================================
#  Alembic setup
# ============================================================

alembic_cfg = context.config
fileConfig(alembic_cfg.config_file_name)

# ============================================================
#  Override DATABASE_URL từ .env sang sync driver
#
#  .env dùng:       postgresql+asyncpg://...  (cho FastAPI)
#  Alembic dùng:    postgresql+psycopg2://... (chạy sync)
#
#  Chỉ cần 1 DATABASE_URL trong .env,
#  env.py tự convert sang psycopg2 khi migrate.
# ============================================================

sync_url = os.getenv("DATABASE_URL", "").replace(
    "postgresql+asyncpg", "postgresql+psycopg2"
)
# configparser dùng % cho interpolation → escape %→%% để tránh ValueError
alembic_cfg.set_main_option("sqlalchemy.url", sync_url.replace("%", "%%"))

target_metadata = Base.metadata


# ============================================================
#  include_object — lọc chỉ track 4 schema của project
#
#  PostgreSQL có nhiều schema hệ thống: pg_catalog,
#  information_schema, pg_toast...
#  Nếu không lọc → Alembic cố migrate cả system schema → lỗi.
# ============================================================

TRACKED_SCHEMAS = {"public", "staging", "core", "log"}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        if name == "alembic_version":
            return False
        schema = getattr(object, "schema", None) or "public"
        return schema in TRACKED_SCHEMAS
    return True


# ============================================================
#  Offline mode
#
#  Sinh SQL script ra stdout, KHÔNG kết nối DB thật.
#  Dùng để review migration trước khi apply lên production.
#
#  Chạy:
#    alembic upgrade head --sql > migration_review.sql
# ============================================================

def run_migrations_offline() -> None:
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
        # Bảng alembic_version (lưu migration history) đặt ở public
        version_table_schema="public",
    )
    with context.begin_transaction():
        context.run_migrations()


# ============================================================
#  Online mode
#
#  Kết nối DB thật và chạy migration trực tiếp.
#
#  Chạy:
#    alembic revision --autogenerate -m "init all schemas"
#    alembic upgrade head
# ============================================================

def run_migrations_online() -> None:
    connectable = engine_from_config(
        alembic_cfg.get_section(alembic_cfg.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    # Tạo schema trong connection riêng, commit xong đóng hẳn trước khi migrate.
    # Không dùng chung connection với migration vì commit() giữa chừng
    # phá vỡ transaction state → alembic_version không được tạo đúng cách.
    with connectable.connect() as setup_conn:
        for schema in ["staging", "core", "log"]:
            setup_conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        setup_conn.commit()

    # Connection sạch hoàn toàn cho migration — Alembic tự quản lý transaction.
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object,
            version_table_schema="public",
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()