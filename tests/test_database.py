from src.database.database import Database
import pytest
import psycopg2

def test_database_connection_success(db_params):
    db = Database(**db_params, _use_singleton=False)
    assert db.connection is not None
    assert db.connection.closed == 0
    db.close()

def test_database_singleton_behavior(db_params):
    db1 = Database(**db_params)
    db2 = Database(**db_params)
    assert db1 is db2
    assert db1.connection is db2.connection
    db1.close()
    db2.close()

    Database.reset_instance()

def test_database_non_singleton_behavior(db_params):
    db1 = Database(**db_params, _use_singleton=False)
    db2 = Database(**db_params, _use_singleton=False)
    assert db1 is not db2
    db1.close()
    db2.close()

def test_invalid_database_password(db_params):
    with pytest.raises(psycopg2.OperationalError):
        Database(
            db_params["dbname"],
            db_params["user"],
            "incorrect_password",
            db_params["host"],
            db_params["port"],
            _use_singleton=False,
        )

def test_invalid_database_username(db_params):
    with pytest.raises(psycopg2.OperationalError):
        Database(
            db_params["dbname"],
            "invalid_username",
            db_params["password"],
            db_params["host"],
            db_params["port"],
            _use_singleton=False,
        )
