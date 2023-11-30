import pytest as pytest
from sqlalchemy import create_engine
from tenacity import retry, stop_after_delay
from sqlalchemy.orm import sessionmaker, clear_mappers
from allocation import config
from allocation.adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db():
    engine = create_engine('sqlite:///:memory:')
    metadata.create_all(engine)
    return engine

@pytest.fixture
def session_factory(in_memory_db):
    start_mappers()
    yield sessionmaker(bind=in_memory_db)
    clear_mappers()

@pytest.fixture
def session(session_factory):
    return session_factory()


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
