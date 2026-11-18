"""Fixtures compartidas: cada prueba usa una base SQLite nueva en memoria."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import Base, get_session
from app.main import app
from app.storage import get_upload_dir


@pytest.fixture
def sesiones():
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, expire_on_commit=False)
    engine.dispose()


@pytest.fixture
def carpeta(tmp_path):
    return tmp_path


@pytest.fixture
def client(sesiones, carpeta):
    def get_session_de_prueba():
        with sesiones() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_de_prueba
    app.dependency_overrides[get_upload_dir] = lambda: carpeta
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
