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

    def get_primary_key_column(self, table):
        """
           Retrieves the primary key column name(s) of a PostgreSQL table.

           This method queries PostgreSQL system catalogs (`pg_index` and `pg_attribute`)
           to determine the primary key defined for a table. It supports both simple
           primary keys (one column) and composite primary keys (multiple columns).

           Args:
               table (str):
                   Name of the table whose primary key should be retrieved.

           Returns:
               str | list[str]:
                   - If the table has a single-column primary key, returns the column name as a string.
                   - If the table has a composite primary key, returns a list of column names.

           Raises:
               ValueError:
                   If the table does not have a primary key defined.
        """
        query = """
            SELECT a.attname
            FROM   pg_index i
            JOIN   pg_attribute a 
                   ON a.attrelid = i.indrelid
                  AND a.attnum = ANY(i.indkey)
            WHERE  i.indrelid = %s::regclass
            AND    i.indisprimary;
        """

        with self.connection.cursor() as cursor:
            cursor.execute(query, (table,))
            rows = cursor.fetchall()

        if not rows:
            raise ValueError(f"Table '{table}' has no primary key.")

        # Si la PK es compuesta, devolver lista
        if len(rows) > 1:
            return [r[0] for r in rows]

        # Si es solo una PK (caso común)
        return rows[0][0]

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

    def select_record_by_id(self, table, id):
        """
           Selects a single record from a table using its primary key.

           This method automatically determines the table's primary key column
           using `get_primary_key_column`, and performs a secure, parameterized
           SELECT to retrieve the row corresponding to the given primary key value.

           Args:
               table (str):
                   Name of the table to query.
               id (Any):
                   Value of the primary key for the record to retrieve.

           Returns:
               dict | None:
                   - A dictionary representing the row (column_name → value) if found.
                   - None if no row exists with the given primary key.
            Raises:
                ValueError:
                    If the table does not have a primary key.
                psycopg2.Error:
                    If the database query fails.
        """
        id_col = self.get_primary_key_column(table)

        query = sql.SQL("SELECT * FROM {table} WHERE {id_col} = %s").format(
            table=sql.Identifier(table),
            id_col=sql.Identifier(id_col)
        )

        with self.connection.cursor() as cursor:
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            if not row:
                return None

            col_names = [desc[0] for desc in cursor.description]
            return dict(zip(col_names, row))

    def update_record_by_id(self, table, id, dict_new_values=None, columns=None, new_values=None):
        """
        Updates a single record in a table by its primary key.

        Allows two calling styles:
            - dict_new_values={"col": value}
            - columns=["col1", "col2"], new_values=[v1, v2]

        Ignores internal columns prefixed with "_".
        """

        id_col = self.get_primary_key_column(table)

        # Ensure record exists
        existing = self.select_record_by_id(table, id)
        if existing is None:
            raise ValueError(f"Record with primary key id {id} not found.")

        # ===== Build dict_new_values =====
        # Case 1: user sent a dict
        if dict_new_values is not None:
            if columns or new_values:
                raise ValueError("columns and new_values must be None when dict_new_values is used")
            if not isinstance(dict_new_values, dict):
                raise TypeError("dict_new_values must be a dict")
        else:
            # Case 2: user sent columns + new_values
            if columns is None or new_values is None:
                raise ValueError("Either dict_new_values OR (columns + new_values) must be provided")
            if len(columns) != len(new_values):
                raise ValueError("columns and new_values must be of same length")
            dict_new_values = {c: v for c, v in zip(columns, new_values)}

        # Remove internal columns
        dict_new_values = {col: val for col, val in dict_new_values.items()
                           if not col.startswith("_")}

        # Ensure something to update
        if not dict_new_values:
            raise ValueError("No valid columns to update (only internal or empty).")

        columns = list(dict_new_values.keys())
        new_values = list(dict_new_values.values())

        # Perform update
        updated_rows = self.update_records(
            table=table,
            columns=columns,
            values=new_values,
            where_columns=[id_col],
            where_operators=["="],
            where_values=[id]
        )

        # update_records returns list of dicts
        return updated_rows[0] if updated_rows else None

    from psycopg2 import sql

    def select_unique_record(self, table, **conditions):
        """
        Selects a single unique record from a table based on the given conditions.

        Parameters
        ----------
        table : str
            The name of the table to query.
        **conditions : dict
            Column-value pairs to use in the WHERE clause.
            Example: select_unique_record("Sites", col1="value1", col2="value2")

        Returns
        -------
        dict or None
            - The unique record as a dictionary if exactly one record matches.
            - None if no records match.

        Raises
        ------
        ValueError
            If more than one record matches the given conditions.
        """

        if not conditions:
            raise ValueError("At least one condition must be provided.")

        # Build WHERE clause
        where_columns = []
        where_operators = []
        where_values = []

        for col, val in conditions.items():
            where_columns.append(col)
            where_operators.append("=")
            where_values.append(val)

        # Build SQL query
        where_clauses = [
            sql.SQL("{} {} %s").format(sql.Identifier(col), sql.SQL(op))
            for col, op in zip(where_columns, where_operators)
        ]

        query = sql.SQL("SELECT * FROM {} WHERE ").format(sql.Identifier(table)) + \
                sql.SQL(" AND ").join(where_clauses)

        with self.connection.cursor() as cursor:
            cursor.execute(query, where_values)
            rows = cursor.fetchall()

        if len(rows) == 0:
            return None
        if len(rows) > 1:
            raise ValueError(
                f"Expected exactly one record, but found {len(rows)} for conditions {conditions}"
            )

        # Convert row to dict
        col_names = [desc[0] for desc in cursor.description]
        return dict(zip(col_names, rows[0]))