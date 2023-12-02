import time
from pathlib import Path

import pytest as pytest
import requests
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker, clear_mappers

from allocation import config
from allocation.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    # engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///:memory:', echo=False)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()


@pytest.fixture
def sqlite_db():
    # engine = create_engine('sqlite:///', echo=True)
    engine = create_engine(config.get_sqlite_uri())
    metadata.create_all(engine)
    return engine


@pytest.fixture
def session(session_factory):
    return session_factory()


@pytest.fixture
def sqlite_session_factory(sqlite_db):
    start_mappers()
    yield sessionmaker(bind=sqlite_db)
    clear_mappers()


@pytest.fixture
def sqlite_session(sqlite_session_factory):
    return sqlite_session_factory()


# @retry(stop=stop_after_delay(10))
# def wait_for_postgres_to_come_up(engine):
#     return engine.connect()
#
#
# @pytest.fixture(scope='session')
# def postgres_db():
#     print('postgres_db')
#     engine = create_engine(config.get_sqlite_uri())
#     wait_for_postgres_to_come_up(engine)
#     metadata.create_all(engine)
#     return engine

def wait_for_webapp_to_come_up():
    deadline = time.time() + 10
    url = config.get_api_url()
    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    pytest.fail("API never came up")


@pytest.fixture
def add_stock(sqlite_session):
    batches_added = set()
    skus_added = set()

    session = sqlite_session

    def _add_stock(lines):
        for reference, sku, qty, eta in lines:
            session.execute(
                text("INSERT INTO batches (reference, sku, _purchased_quantity, eta)"
                     " VALUES (:reference, :sku, :qty, :eta)"),
                dict(reference=reference, sku=sku, qty=qty, eta=eta),
            )
            [[batch_id]] = session.execute(
                text("SELECT id FROM batches WHERE reference=:reference AND sku=:sku"),
                dict(reference=reference, sku=sku),
            )

            batches_added.add(batch_id)
            skus_added.add(sku)
        session.commit()

    yield _add_stock

    for batch_id in batches_added:
        session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id),
        )
        session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"), dict(batch_id=batch_id),
        )
    for sku in skus_added:
        session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"), dict(sku=sku),
        )
    session.commit()


@pytest.fixture
def restart_api():
    (Path(__file__).parent / "../src/allocation/api/flask/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
