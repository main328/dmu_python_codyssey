import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# -----------------------------------------------------------------
# [수정] 현재 작업 경로(backend)를 시스템 경로에 추가
# -----------------------------------------------------------------
sys.path.append(os.getcwd())

# -----------------------------------------------------------------
# [수정] 모델과 Base 객체 임포트 (초기화로 인해 사라진 부분 복구)
# -----------------------------------------------------------------
import models               # models.py (테이블 정보가 담김)
from database import Base   # database.py (Base 객체가 담김)

# Alembic Config 객체
config = context.config

# 로깅 설정
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -----------------------------------------------------------------
# [수정] target_metadata 연결
# models.Base.metadata 대신 database.Base.metadata를 사용
# -----------------------------------------------------------------
target_metadata = Base.metadata

# (이하 코드는 Alembic 기본 설정입니다)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()