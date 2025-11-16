import traceback

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

    def insert_record(self, table, columns, values, autocommit=False):
        """
        Inserts a record into the specified table using the given columns and values.
        Column names starting with an underscore (_) are excluded from the insert operation.

        Args:
            table: table name within the database.
            columns: name of the columns within the table.
            values: values to be inserted.
            autocommit: autocommit the insert operation.
        Returns:
             inserted_record: dictionary with the inserted record.
        """
        record = {
            col: value for col, value in zip(columns, values)
            if not col.startswith("_")
        }
        n_columns = len(record)

        sql_statement = sql.SQL("""
        INSERT INTO {table} ({fields}) VALUES ({placeholders})
        RETURNING *
        """).format(
            table=sql.Identifier(table),
            fields=sql.SQL(", ").join((map(sql.Identifier, record.keys()))),
            placeholders=sql.SQL(", ").join(sql.Placeholder() * n_columns),
        )

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(sql_statement, list(record.values()))
                row = cursor.fetchone()
                if row is None:
                    raise RuntimeError("Insert failed: no row returned")

                col_names = [desc[0] for desc in cursor.description]
                inserted_record = dict(zip(col_names, row))
            if autocommit:
                self.commit()
            return inserted_record
        except Exception as e:
            raise

    def select_records(self, table, columns='*', where_columns=None, where_operators=None, where_values=None):
        """
        Selects records from the specified table with optional WHERE conditions.
        If the select contains WHERE conditions, each condition must be passed separated in a value of lists
        where_columns, where_operators, and where_values


        Args:
            table (str): The name of the table to select from.
            columns (str or list of str): Columns to select. Defaults to '*' for all columns.
            where_clause (str, optional): A WHERE clause with placeholders (e.g., "age > %s AND active = %s").
            where_values (list, optional): A list of values to fill in the placeholders in the WHERE clause.

        Returns:
            list[tuple]: A list of rows (tuples) returned by the query.

        Raises:
            Exception: Propagates database-related exceptions if the query fails.
        """
        if isinstance(columns, list):
            columns_sql = sql.SQL(', ').join(map(sql.Identifier, columns))
        else:
            if columns.strip() == '*':
                columns_sql = sql.SQL('*')
            else:
                # Columns value as string: e.g.: 'col1, col2, col3'
                columns_split = [col.strip() for col in columns.split(',')]
                columns_sql = sql.SQL(', ').join(map(sql.Identifier, columns_split))

        query = sql.SQL("SELECT {fields} FROM {table}").format(
            fields=columns_sql,
            table=sql.Identifier(table)
        )

        # ===== build WHERE clause =====
        if where_columns:
            if not (len(where_columns) == len(where_operators) == len(where_values)):
                raise ValueError("where_columns, where_operators, and where_values must have same length")

            sql_conditions = []
            for col, op in zip(where_columns, where_operators):
                sql_conditions.append(
                    sql.SQL("{col} {op} %s").format(
                        col=sql.Identifier(col),
                        op=sql.SQL(op)
                    )
                )

            where_sql = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(sql_conditions)
            query = query + where_sql

        # ===== Execute SQL query =====
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, where_values or [])

                col_names = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()


                return [dict(zip(col_names, row)) for row in rows]

        except Exception as e:
            raise

    def update_records(self, table, columns, values, where_columns=None, where_operators=None, where_values=None):
        """
        Updates records in the given table using safe SQL composition.

        Args:
            table (str): Table name.
            columns (list[str]): List of columns to update.
            values (list): Values corresponding to each column.
            where_columns (list[str], optional): Columns to filter.
            where_operators (list[str], optional): Operators (=, >, <, LIKE, etc).
            where_values (list, optional): Values for WHERE conditions.

            Returns:
                list[dict]: Updated records.
        """
        if len(columns) != len(values):
            raise ValueError("columns, values must have same length")
        if where_columns or where_operators or where_values:
            if not len(where_columns) == len(where_operators) == len(where_values):
                raise ValueError("where_columns, where_operators, where_values must have same length")


        # ===== build SQL query =====

        # -> Set clause
        set_clause = sql.SQL(", ").join(
            sql.SQL("{} = {}").format(sql.Identifier(col), sql.Placeholder())
            for col in columns
        )
        params = list(values)

        # -> where clause
        where_clause = sql.SQL("")
        if where_columns:
            where_parts = []
            for col, op in zip(where_columns, where_operators):
                where_parts.append(
                    sql.SQL("{} {} {}").format(
                        sql.Identifier(col),
                        sql.SQL(op),
                        sql.Placeholder()
                    )
                )
            where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_parts)
            params.extend(where_values)

        # -> Final query
        query = sql.SQL("UPDATE {table} SET {set_clause}{where_clause} RETURNING *").format(
            table=sql.Identifier(table),
            set_clause=set_clause,
            where_clause=where_clause,
        )

        # Execute query
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                return [dict(zip(col_names, row)) for row in rows]

        except Exception as e:
            raise

    def delete_records(self, table, where_columns=None, where_operators=None, where_values=None):
        """
        Deletes records from the given table using safe SQL composition.

        Args:
            table (str): Table name.
            where_columns (list[str], optional): Columns to filter.
            where_operators (list[str], optional): Operators (=, >, <, LIKE, etc).
            where_values (list, optional): Values for WHERE conditions.

        Returns:
            list[dict]: Deleted records.
        """
        # Validate WHERE clause lengths
        if where_columns or where_operators or where_values:
            if not (len(where_columns) == len(where_operators) == len(where_values)):
                raise ValueError("where_columns, where_operators, where_values must have same length")
        else:
            raise ValueError("DELETE without WHERE clause is not allowed for safety")

        # ===== build SQL query =====

        # -> where clause
        where_parts = []
        for col, op in zip(where_columns, where_operators):
            where_parts.append(
                sql.SQL("{} {} {}").format(
                    sql.Identifier(col),
                    sql.SQL(op),
                    sql.Placeholder()
                )
            )

        where_clause = sql.SQL(" WHERE ") + sql.SQL(" AND ").join(where_parts)
        params = list(where_values)

        # -> Final query
        query = sql.SQL("DELETE FROM {table}{where_clause} RETURNING *").format(
            table=sql.Identifier(table),
            where_clause=where_clause,
        )

        # Execute query
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                rows = cursor.fetchall()
                col_names = [desc[0] for desc in cursor.description]
                return [dict(zip(col_names, row)) for row in rows]

        except Exception:
            raise