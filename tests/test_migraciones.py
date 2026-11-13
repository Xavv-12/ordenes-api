"""Comprueba que las migraciones de Alembic crean las tablas en una base vacía."""

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, inspect


def test_las_migraciones_crean_las_tablas(tmp_path):
    url = f"sqlite:///{tmp_path / 'prueba.db'}"
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", url)  # una base temporal, no ordenes.db

    command.upgrade(config, "head")

    tablas = inspect(create_engine(url)).get_table_names()
    assert {"orders", "comprobantes"} <= set(tablas)

    command.downgrade(config, "base")  # y también se pueden revertir
    assert inspect(create_engine(url)).get_table_names() == ["alembic_version"]
