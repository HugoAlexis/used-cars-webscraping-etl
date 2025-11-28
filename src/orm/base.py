from ..database.database import  Database

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

    table_name = ""
    table_columns = []
    table_id = []
    _db_object = None          # Use only for testing

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
        for k, v in kwargs.items():
            if k in self.table_columns:
                setattr(self, k, v)
            else:
                raise ValueError(f"Column {k} is not present in the model")

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
                dbname="xxxxx",
                user='xxxxx',
                password='',
                host='xxxxx',
                port='xxxxx',
            )
        except Exception:
            # Placeholder while development environment isn't configured yet
            return "NotImplemented"


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
        return {col: getattr(self, col, None) for col in self.table_columns}

    def dump(self):
        """
        Insert the current object into the database table associated with the model.

        Returns:
            list:
                A list containing the primary key values corresponding to `table_id`,
                in the same order as defined in the class.

        Behavior:
            - Converts the model's public attributes (`dict_record`) to column/value lists.
            - Calls the database method:
                insert_record(table, columns, values) -> dict
            - Expects the returned dict to contain the values for all primary key columns.

        Raises:
            Various exceptions may propagate from the database backend, such as:
                - integrity errors
                - connection issues
                - schema mismatches

        Example:
            site = Site(name="A", base_url="http://a.com")
            pk = site.dump()   # → ["generated_id"]
        """
        dict_record = {col: val for col, val in self.dict_record.items()
                       if col in self.table_columns and not col in self.table_id}

        record = self.db().insert_record(
            table=self.table_name,
            columns=list(dict_record.keys()),
            values=list(dict_record.values()),
        )

        record_id = []
        for col_id in self.table_id:
            record_id.append(record[col_id])
        return record_id

    @classmethod
    def from_id_in_database(cls, record_id):
        """
        Retrieve a single record from the database using its primary key.

        Parameters:
            record_id (list):
                A list of primary key values in the same order as defined by `table_id`.

        Returns:
            BaseModel:
                An instance of the model populated with the retrieved database record.

        Raises:
            ValueError:
                If the number of key values does not match `table_id`, or if the record
                does not exist in the database.

            NotImplementedError:
                If the model uses a composite primary key (more than one column).
                Extended support is required for future expansion.

        Database requirements:
            The database object must implement:
                select_record_by_id(table: str, id: Any) -> dict|None

        Example:
            site = Site.from_id_in_database([1])
        """

        if len(record_id) != len(cls.table_id):
            raise ValueError("Number of elements in `record_id` does not match the number of columns in `table_id`.")

        if len(cls.table_id) != 1:
            raise NotImplementedError

        record = cls.db().select_record_by_id(table=cls.table_name, id=record_id[0])
        print(record)
        if record:
            return cls(**record)
        else:
            raise ValueError(f"Id {record_id} does not correspond to any record in the database.")

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