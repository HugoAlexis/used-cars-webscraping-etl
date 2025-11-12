import psycopg2
from psycopg2 import sql

class Database:
    """
    Singleton class that handles database connection and
    functionality.
    """
    _instance = None
    def __new__(cls, *args, **kwargs):
        """
        Creates a new instance of the database class. If _use_singleton is True (the default),
        the object is implemented as a Singleton.
        :param args:
        :param kwargs:
        """
        use_singleton = kwargs.pop("_use_singleton", True)

        # Avoid singleton pattern (for testing)
        if not use_singleton:
            instance = super().__new__(cls)
            instance._init_connection(*args, **kwargs)
            instance.__initialized = False
            return instance

        # Define singleton pattern
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.__initialized = False
            cls._instance._init_connection(*args, **kwargs)
        return cls._instance

    def _init_connection(self, dbname, user, password, host, port):
        self._connection = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port,
        )
        self._connection.autocommit = False

    @classmethod
    def reset_instance(cls):
        """
        Rest the singleton instance (useful for testing).
        """
        if cls._instance is not None:
            if hasattr(cls._instance, "_connection") and not cls._instance._connection.closed:
                cls._instance.connection.close()
            cls._instance = None

    @property
    def connection(self):
        """
        Returns the connection to the database.
        :return: psycopg.connection
        """
        return self._connection

    def commit(self):
        """
        Commits the current transaction to the database.
        :return: None
        """
        self.connection.commit()

    def rollback(self):
        """
        Rollback the current transaction to the database.
        :return: None
        """
        self.connection.rollback()

    def close(self):
        """
        Closes the database connection.
        """
        if self._connection and not self._connection.closed:
            self._connection.close()
