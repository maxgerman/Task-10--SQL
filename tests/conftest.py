"""Test configuration and fixtures. For tests the newly created db is used, one for the whole testing session"""

import pytest
import sqlalchemy.engine
from sqlalchemy_utils.functions import database_exists, create_database

from src import db
from src.db import engine, create_engine
from src.app import app


@pytest.fixture(scope='session', autouse=True)
def test_db() -> sqlalchemy.engine.Engine:
    """Create the new engine with test URL for testing, replace the original one and insert initial data to test db.

    Only one db is used for the testing session.
    Set engine echo=True for sqlalchemy output in stdout during testing"""

    before, _, after = str(engine.url).rpartition('/')
    test_db_url = before + '/test_' + after
    test_engine = create_engine(test_db_url, echo=False, future=True)
    db.engine = test_engine
    if not database_exists(test_engine.url):
        create_database(test_engine.url)
    db.insert_initial_data()
    return test_engine


@pytest.fixture()
def test_client():
    """Return Flask test client for API testing"""
    return app.test_client()
