import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from dotenv import load_dotenv
from src.database.database import Database

load_dotenv(".env.testing")

@pytest.fixture(scope="session")
def db_params():
    """
    Fixture with the params for database connection
    """
    return {
        "dbname": "used_cars_test",
        "user": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

# Clean singleton instance for test independence
@pytest.fixture(autouse=True)
def cleanup_database_instance():
    yield
    Database.reset_instance()

@pytest.fixture(scope="function")
def db_instance():
    """
    Fixture with database object.
    :return: Database object.
    """
    db = Database(
        dbname= "used_cars_test",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        _use_singleton=False
    )
    with db.connection.cursor() as cursor:
        cursor.execute("BEGIN;")
    try:
        yield db
    finally:
        db.connection.rollback()