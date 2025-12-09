import datetime
from src.orm.base import  BaseORMModel
from src.database.database import  Database
import os
now = datetime.datetime.now

class SiteTest(BaseORMModel):
    table_name = 'sites_testing'
    table_id = ['site_id']
    table_columns = ['site_id', 'name', 'base_url', 'created_at', 'updated_at']
    _db_object = Database(
        dbname= "used_cars_webscraping_test",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        _use_singleton=True
    )

    def __init__(self, name, base_url, **kwargs):
        super().__init__(
            name=name,
            base_url=base_url,
            **kwargs
        )


class Table1Test(BaseORMModel):
    table_name = 'table_1'
    table_id = ['t1_id']
    table_columns = ['t1_id', 'name_t1']
    _db_object = Database(
        dbname="used_cars_webscraping_test",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        _use_singleton=True
    )

    def __init__(self, name_t1, **kwargs):
        super().__init__(name_t1=name_t1, **kwargs)


class Table2Test(BaseORMModel):
    table_name = 'table_2'
    table_id = ['t2_id']
    table_columns = ['t2_id', 'name_t2']
    _db_object = Database(
        dbname="used_cars_webscraping_test",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        _use_singleton=True
    )

    def __init__(self, name_t2, **kwargs):
        super().__init__(name_t2=name_t2, **kwargs)


class JointTable1Table2Test(BaseORMModel):
    table_name = 'joint_table1_table2'
    table_columns = ['t1_id', 't2_id']
    _db_object = Database(
        dbname="used_cars_webscraping_test",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        _use_singleton=True
    )

    def __init__(self, t1_id, t2_id, **kwargs):
        super().__init__(t1_id=t1_id, t2_id=t2_id, **kwargs)
