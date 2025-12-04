import os
import psycopg2
from psycopg2 import sql
import dotenv

dotenv.load_dotenv(".env")


def get_credentials():
    """
    Retrieve PostgreSQL credentials from environment variables.

    This function reads `DB_USERNAME` and `DB_PASSWORD` from the
    environment (`.env` file) and returns them as a tuple.

    Returns:
       tuple[str, str]
           A tuple containing (username, password) for connecting to PostgreSQL.
    """
    return (
        os.getenv("DB_USERNAME"),
        os.getenv("DB_PASSWORD")
    )


def check_database_exists(dbname):
    """
    Check whether a PostgreSQL database exists.

    This function connects to the default 'postgres' database and queries
    the system catalog `pg_database` to determine whether a database with
    the provided name exists.

    Params:
        * dbname : str
            The name of the database to check.

    Returns:
        bool
            True if the database exists, False otherwise.

    Raises:
        psycopg2.OperationalError
            If the connection to the PostgreSQL server fails.
    """
    user, password = get_credentials()

    # Connection to existing Database
    with psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host="localhost",
        port=5432
    ) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
            return cur.fetchone() is not None


def create_database(dbname):
    """
    Create a new PostgreSQL database if it does not already exist.

    This function connects to the default 'postgres' database and executes
    a CREATE DATABASE statement safely using psycopg2 SQL identifiers.
    If the database already exists, a `DuplicateDatabase` error is caught
    and a message is printed.

    Params:
        dbname : str
            The name of the database to create.

    Returns:
        None

    Raises:
        psycopg2.errors.DuplicateDatabase
            If the database already exists. This is handled internally.
        Exception
            For any other unexpected SQL or connection errors.
    """

    user, password = get_credentials()

    conn = psycopg2.connect(
        dbname="postgres",
        user=user,
        password=password,
        host="localhost",
        port=5432
    )
    conn.autocommit = True

    with conn.cursor() as cur:
        try:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(dbname)))
            print(f"Database '{dbname}' created successfully.")
        except psycopg2.errors.DuplicateDatabase:
            print(f"Database '{dbname}' already exists. Skipping.")
        except Exception as e:
            print("Error while creating database.")
            raise e


def initialize_database_schema(dbname, sql_file="sql/create_schema.sql"):
    """
    Apply the SQL schema from a file to the specified PostgreSQL database.

    This function reads the SQL statements from `sql/create_schema.sql` and
    executes them on the target database. It is typically used right after
    creating a new database to set up tables, indexes, relationships, or
    any other schema definitions.

    Params:
        dbname : str
            The name of the database where the schema will be applied.

    Returns:
        None

    Raises:
        FileNotFoundError
            If the SQL schema file cannot be found.
        Exception
            If an error occurs while executing the SQL schema.
    """
    user, password = get_credentials()

    # Leer archivo SQL de forma segura
    with open(sql_file, "r") as f:
        sql_schema = f.read()

    with psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host="localhost",
        port=5432
    ) as conn:
        with conn.cursor() as cur:
            try:
                cur.execute(sql_schema)
                print(f"Schema applied successfully to '{dbname}'.")
            except Exception as e:
                print("Error applying schema.")
                raise e

        conn.commit()