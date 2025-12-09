import os
from datetime import datetime
from ..database.database import  Database
from psycopg2.errors import ConnectionFailure
now = datetime.now


class BaseORMModel:
    """
    Base class for Object-Relational Mapping (ORM) models

    This class defines the core functionality and interface that all ORM subclasses must implement.
    It provides general methods for interacting with the database, such as inserting an object
    (`dump`), updating an existing record (`update`), creating an instance from a database record
    (`from_database`), and creating an instance from a parser object (`from_parser`).

    Subclasses must define the following class attributes:
        - `table_name` (str): Name of the associated database table.
        - `table_columns` (list of str): Valid column names for the table.
        - `table_id` (list of str): Column names that make up the primary key.

    Subclass constraints:
        - All mandatory database columns must match an instance attribute or property,
          accessible via <cls>.<column_name>
        - All extra instance attributes must start with _ or __ to be ignored by ORM methods.

    Available methods:
        - dump(): Insert the object into the database.
        - update(): Update the existing database record using the primary key.
        - from_parser(): Create an ORM instance from a parser object.
    """

    # Mandatory class attributes (must be defined in all subclasses)
    table_name = ""
    table_columns = []
    table_id = []

    # General class attributes
    ignored_columns_in_dict_record = ['updated_at', 'created_at']        # Columns ignored in
    _db_object = None          # Use only for testing
    _dbname = None

    def __init_subclass__(cls):
        # Verify table_columns is defined
        if not cls.table_columns:
            raise TypeError(f"{cls.__name__} must define class attribute 'table_columns'")
        if not isinstance(cls.table_columns, (list, tuple)):
            raise TypeError(f"{cls.__name__}.table_columns must be a list or tuple")

        # Verify fields defined in table_columns are strings, and don't start with '_'
        for col in cls.table_columns:
            if not isinstance(col, str):
                raise TypeError(f"{cls.__name__}.table_columns items must be strings")
            if col.startswith("_"):
                raise ValueError(f"{cls.__name__}.table_columns contains private column '{col}")

        # Verify table_id
        if not isinstance(cls.table_id, (list, tuple)):
            raise TypeError(
                f"{cls.__name__}.table_id must be a list or tuple"
            )

        # List of primary key(s) must be defined in table_columns
        for key in cls.table_id:
            if key not in cls.table_columns:
                raise ValueError(
                    f"{cls.__name__}.table_id contains '{key}' "
                    f"which is not present in table_columns"
                )

    def __init__(self, **kwargs):
        """
        Initialize a model instance with keyword arguments corresponding to the model's table columns.

        Parameters:
            **kwargs:
                Key-value pairs where each key must match a name in `table_columns`.
                Keys not present in `table_columns` are silently ignored.

        Behavior:
            - Only attributes listed in `table_columns` are assigned.
            - Private/internal attributes (starting with "_") are not auto-populated.

        Example:
            Site(name="Example", base_url="http://example.com")
        """
        self._is_dumped = False
        if 'created_at' in self.table_columns:
            created_at = kwargs.pop('created_at', now())
            self.created_at = created_at
        if 'updated_at' in self.table_columns:
            updated_at = kwargs.pop('updated_at', None)
            self.updated_at = updated_at
        for k, v in kwargs.items():
            if k in self.table_columns:
                setattr(self, k, v)
            else:
                raise ValueError(f"Column {k} is not present in the model")


    def __repr__(self):
        return ''
        repr_record = (
                '-' * 30 + '\n' +
                f'<<<  {self.__class__.__name__} record  >>>\n' +
                f'Dumped: {self.is_dumped}\n\n' +
                '\n'.join([f'|{"*" if col in self.table_id else "-"}  {col} = {value}' for col, value in self.dict_record.items()]) +
                '\n' + '-' * 30 + '\n'
        )
        return repr_record

    def __str__(self):
        return self.__repr__()


    @classmethod
    def db(cls):
        """
        Return the Database singleton object used for database connection.

        During unit tests, `_db_object` should be injected externally to isolate test behavior from production
        database.

        Behavior:
            - If `_db_object` is explicitly set (e.g., in tests), return it.
            - Otherwise, attempt to create or return the global `Database` singleton.
            - If the global Database cannot be created due to missing configuration
              (e.g., missing .env), return a temporary placeholder.

        Returns:
            Database | str:
                The configured database object, or a placeholder string while
                the real configuration is not yet available.
        """

        # If tests injected a DB object, return it immediately
        if cls._db_object is not None:
            return cls._db_object

        # Production: attempt to instantiate the global Database singleton
        try:
            return Database(
                dbname=cls._dbname,
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
            )
        except Exception:
            raise ConnectionFailure("Failure trying to connect to Database")


    @classmethod
    def all(cls):
        """
        Retrieve all records from the database table associated with the model.

        Returns:
            list[BaseModel]:
                A list of model instances populated with the data retrieved
                from the database.

        Example:
            sites = Site.all()
        """
        records = cls.db().select_records(table=cls.table_name)
        return [cls(**r) for r in records]


    @property
    def dict_record(self):
        """
        Return a dictionary representation of the object's public ORM-managed data.

        Returns:
            dict:
                A mapping of column names to values for all attributes that:
                - do NOT start with "_"
                - are present in the class table_columns

        Notes:
            - Private attributes (e.g., _internal) are excluded by design.
            - Only attributes that exist on the class attribute 'table_columns' are included.
            - Useful INSERT or UPDATE operations, or for representation.

        Example:
            site = Site(name="A", base_url="http://a.com")
            site.dict_record
            # → {"name": "A", "base_url": "http://a.com"}
        """
        columns = [col for col in self.table_columns if not col in self.ignored_columns_in_dict_record]
        return {col: getattr(self, col, None) for col in columns}


    @property
    def is_dumped(self):
        """
        Indicates whether this instance has already been persisted to the database.

        Returns:
            bool:
                True if the model was previously inserted into the database through
                an ORM operation (e.g., `dump()`), False otherwise.

        Notes:
            - This flag is maintained internally by the ORM and should not be
              modified manually.
            - A value of True does not guarantee that a corresponding record still
              exists in the database (e.g., it may have been deleted externally).
            - This property is intended to prevent redundant insertions of the same
              in-memory object.
        """
        return self._is_dumped

    @property
    def record_exists(self):
        """
            Checks whether a record with the same attribute values already exists
            in the database, excluding primary key fields.

            The comparison is performed using the object's `dict_record` attribute,
            filtered to remove the primary key columns defined in `table_id`. The
            remaining fields are used to query the database through
            `select_unique_record()`.

            Returns:
                bool:
                    True if a matching record exists in the database, False otherwise.

            Notes:
                - For instances created manually (e.g., `obj = MyModel(...)`), this
                  attribute is initialized as False.
                - Methods that load records directly from the database (such as
                  `from_id_in_database`) must set this flag to True.
                - This property is used internally to prevent unintended duplicate
                  insertions into the table.
            """
        dict_record_without_pk = {col: val for col, val in self.dict_record.items() if col not in self.table_id}
        record = self.db().select_unique_record(table=self.table_name, **dict_record_without_pk)

        return bool(record)

    @property
    def pk(self):
        """
        Returns list of primary key values associated with the model.
        """
        pk_val = [getattr(self, col, None) for col in self.table_id]
        return pk_val

    def dump(self, force=False):
        """
            Persist the current model instance into the database table associated with this class.

            This method inserts the record into the database unless a similar record
            already exists (based on non–primary key fields). If a duplicate is detected,
            the method returns the primary key of the existing record instead of inserting
            a new one. This duplicate-avoidance behavior is skipped when `force=True`.

            Parameters:
                force (bool, optional):
                    If False (default), the method prevents duplicate insertion when a
                    record with the same non–primary key fields already exists in the
                    table. When True, the method always inserts a new row, even if an
                    identical record is already present.

            Returns:
                list:
                    A list containing the primary key values corresponding to the model's
                    `table_id`, in the same order in which the primary key columns are
                    defined in the class.

                    - If the record already exists in the database and `force=False`,
                      the method returns the primary key of the existing record.
                    - If a new row is inserted, the method returns the primary key of
                      the newly created row.

            Raises:
                Any exceptions raised by the underlying database backend, including:
                    - Integrity or constraint violations
                    - Connection or operational errors
                    - Missing or unexpected schema fields

            Example:
                site = Site(name="Example", base_url="http://example.com")

                # Insert new record
                pk1 = site.dump()
                # → ["generated_id"]

                # Attempt duplicate insert (but duplicate prevented)
                pk2 = site.dump()
                # → ["generated_id"]   # same PK as pk1

                # Force duplicate insertion
                pk3 = site.dump(force=True)
                # → ["new_generated_id"]
        """
        dict_record = {col: val for col, val in self.dict_record.items()
                       if col in self.table_columns and not col in self.table_id}

        # Avoid duplicates, unless force=True
        if not force and self.record_exists:
            print("Already exists! Not dumping instance")
            record = self.db().select_unique_record(table=self.table_name, **dict_record)
            for col_id in self.table_id:
                setattr(self, col_id, record[col_id])
            # Returns PK of existing record
            return [record[key] for key in self.table_id]

        # Define columns and values to insert record
        columns = list(dict_record.keys())
        values = list(dict_record.values())
        if 'created_at' in self.table_columns:
            columns.append('created_at')
            values.append(getattr(self, 'created_at', None))


        # Inserts record
        record = self.db().insert_record(
            table=self.table_name,
            columns=columns,
            values=values,
        )
        self._is_dumped = True

        record_id = []
        for col_id in self.table_id:
            record_id.append(record[col_id])
            setattr(self, col_id, record[col_id])
        return record_id

    def update(self, columns='*'):
        """
        Updates the current model instance with a new set of column values.
        If columns="*", updates all columns for the record. Specific columns can be updated within the
        record by passing a list of column names (strings) in param columns.
        parameters:
            * columns:
                "*" or list of column names to update.
        Returns:
            * pk
                Primary key value(s) corresponding to updated record instance.
        Raises:
            * ValueError for invalid column parameter.
            * Any exceptions raised by the underlying database backend.
        Example:
            Site = Site(name="Example", base_url="http://site1.com")
            site.dict_values -> {name: "Example", url: "http://example.com"}
            site.base_url = "http://new-site1.com
            site.update()
            site.dict_values -> {name: "Example", url: "http://new-site1.com"}
        """
        # Create column, value pairs to update record
        dict_record = {col: val for col, val in self.dict_record.items()
                       if col in self.table_columns and not col in self.table_id}
        if columns == '*':
            cols = dict_record.keys()
            values = list(dict_record.values())
        elif isinstance(columns, list):
            cols, values = [], []
            for col in columns:
                if not col in self.table_columns:
                    raise ValueError(f"Invalid column name {col}")
                cols.append(col)
                values.append(self.dict_record[col])
        else:
            raise ValueError(f"Invalid column value {columns}")

        update_dict = {col:val for col, val in zip(cols, values)}

        # Add updated_at column if present in cls.table_columns
        if 'updated_at' in self.table_columns:
            updated_at = now()
            update_dict['updated_at'] = updated_at

        # Update operation
        try:
            self.db().update_record_by_id(table=self.table_name, id=self.pk[0], dict_new_values=update_dict)
            self.updated_at = updated_at
        except Exception as e:
            print("Error during updating record")
            raise e
        return self.pk


    @classmethod
    def from_id_in_database(cls, record_id):
        """
        Retrieves a database record by its primary key and returns a model instance
        representing that record.

        Parameters:
            *record_id:
                Primary key value(s) corresponding to this model's `table_id`
                definition.

        Returns:
            BaseModel or None:
                An instance populated with the record data if found.
                The returned instance has its internal `_is_dumped` flag set to True.
                Returns None if no record with the given ID exists.

        Notes:
            - This method should be used when an object must represent an existing
              database row.
            - The instance returned by this method will not trigger new INSERT
              operations if `dump()` is called, unless its data is modified and
              an explicit UPDATE is requested.

        Example:
            site = Site.from_id_in_database([1])
        """

        if len(record_id) != len(cls.table_id):
            raise ValueError("Invalid number of PK values.")

        if len(cls.table_id) != 1:
            raise NotImplementedError("Composite PK not yet implemented.")

        record = cls.db().select_record_by_id(
            table=cls.table_name,
            id=record_id[0]
        )

        if not record:
            raise ValueError(f"Record with ID {record_id} not found.")

        # Crear instancia sin __init__
        instance = object.__new__(cls)

        # Asignar atributos directamente
        for col in cls.table_columns:
            setattr(instance, col, record.get(col))

        # Marcar como persistido
        instance._is_dumped = True

        return instance



    @classmethod
    def from_parser(cls, parser, **kwargs):
        """
        Create a model instance by extracting attributes from a parser object.

        Parameters:
            parser (object):
                Any object exposing attributes named after the model's `table_columns`.

            **kwargs:
                Optional fallback values for columns not present on the parser.

        Returns:
            BaseModel:
                A new instance where each column in `table_columns` is populated from:
                    1) parser.<column> if present, otherwise
                    2) kwargs[column] if given, otherwise
                    3) None

        Behavior:
            - Private columns (starting with "_") are skipped.
            - Attributes on the parser that do not match table columns are ignored.
            - Intended for transforming scraping/parser outputs into ORM records.

        Example:
            parser = SiteParser(name="Example", base_url="http://example.com")
            site = Site.from_parser(parser)
        """
        dict_record = {}
        for col in cls.table_columns:
            if col.startswith("_"): continue
            value = getattr(parser, col, kwargs.get(col, None))
            dict_record[col] = value

        return cls(**dict_record)