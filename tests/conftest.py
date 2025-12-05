import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from dotenv import load_dotenv
from src.database.database import Database
from scripts.initialize_database import *
load_dotenv(".env.testing")

testing_dbname = "used_cars_webscraping_test"

# Create database and apply schema
if not check_database_exists(testing_dbname):
    create_database(testing_dbname)
    initialize_database_schema(testing_dbname)
    initialize_database_schema(testing_dbname, sql_file='sql/schema_and_data_for_testing.sql')


@pytest.fixture(scope="session")
def db_params():
    """
    Fixture with the params for database connection
    """
    return {
        "dbname": testing_dbname,
        "user": os.getenv("DB_USERNAME"),
        "password": os.getenv("DB_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }



@pytest.fixture(scope="function")
def db_instance(db_params):
    """
    Fixture with database object.
    :return: Database object.
    """
    db = Database(**db_params)
    with db.connection.cursor() as cursor:
        cursor.execute("BEGIN;")
    try:
        yield db
    finally:
        db.connection.rollback()