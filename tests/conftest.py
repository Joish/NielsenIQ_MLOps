import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from counter.adapters.helpers import Base, Helpers


@pytest.fixture(scope="session")
def _sqlite_session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(autouse=True)  # applies to every test automatically
def _patch_session_factory(monkeypatch, _sqlite_session_factory):
    # Replace the real Postgres factory with the in-memory one **before** app starts
    monkeypatch.setattr(
        Helpers,
        "create_postgres_session_factory",
        lambda *_args, **_kw: _sqlite_session_factory,
    )
