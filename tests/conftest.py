import time
from pathlib import Path

import pytest as pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, clear_mappers

from allocation import config
from allocation.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()
    clear_mappers()


def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture(scope="session")
def sqlite_db():
    engine = create_engine(config.get_sqlite_uri())
    metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlite_session(sqlite_db):
    start_mappers()
    yield sessionmaker(bind=sqlite_db)()
    clear_mappers()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/allocation/api/flask/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
