import pytest
from sqlalchemy_utils.functions import database_exists, create_database

from src import db
from src.db import engine, create_engine
from src.app import app

TEST_DB_NAME = 'test_students'


@pytest.fixture(scope='session', autouse=True)
def test_db():
    """Set engine echo=True for sqlalchemy output in stdout during testing"""
    before, _, after = str(engine.url).rpartition('/')
    test_db_url = before + '/test_' + after
    test_engine = create_engine(test_db_url, echo=False, future=True)
    db.engine = test_engine
    if not database_exists(test_engine.url):
        create_database(test_engine.url)
    db.insert_initial_data()
    return test_engine


@pytest.fixture(scope='session')
def test_client():
    return app.test_client()


