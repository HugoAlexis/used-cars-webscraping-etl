import datetime
from src.orm.base import  BaseORMModel
from src.database.database import  Database
import os
now = datetime.datetime.now

class SiteTest(BaseORMModel):
    table_name = 'sites'
    table_id = ['site_id']
    table_columns = ['site_id', 'name', 'base_url', 'created_at', 'updated_at']
    _db_object = Database(
        dbname= "used_cars_test",
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        _use_singleton=False
    )

    def __init__(self, name, base_url, **kwargs):
        super().__init__(
            name=name,
            base_url=base_url,
            **kwargs
        )