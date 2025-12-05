from ..orm.base import BaseORMModel

class Site(BaseORMModel):
    table_name = 'sites'
    table_columns = ['site_id', 'name', 'base_url', 'updated_at', 'created_at']
    table_id = ['site_id']

    def __init__(self, name, base_url, **kwargs):
        super().__init__(name=name, base_url=base_url, **kwargs)
