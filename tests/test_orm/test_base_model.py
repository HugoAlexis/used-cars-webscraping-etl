from models_for_test import Site
import pytest

from src.orm.base import BaseORMModel


def test_init_raises_valueerror_for_invalid_columns():
    with pytest.raises(ValueError):
        site = Site(name='site1', base_url='http://example-site1.com', invalid_col="invalid")

def test_basemodel_subclass_no_defines_table_columns():
    with pytest.raises(TypeError):
        class User(BaseORMModel):
            table_name = 'Users'
            table_id = ["user_id"]

def test_table_columns_not_list():
    with pytest.raises(TypeError):
        class User(BaseORMModel):
            table_name = 'user_id,name'
            table_id = ["user_id"]
            table_name="Users"

def test_table_columns_values_invalid_type():
    with pytest.raises(TypeError):
        class User(BaseORMModel):
            table_name = 'Users'
            table_columns = ['user_id', 'name', 123]
            table_id = ["user_id"]

def test_table_id_not_list_or_tuple():
    with pytest.raises(TypeError):
        class User(BaseORMModel):
            table_name = 'Users'
            table_columns = ['user_id', 'name']
            table_id = 'user_id'

def test_table_id_not_in_table_columns():
    with pytest.raises(ValueError):
        class User(BaseORMModel):
            table_name = 'Users'
            table_columns = ['name', 'age']
            table_id = ['user_id']

def test_valid_subclass():
    class User(BaseORMModel):
        table_name = 'Users'
        table_columns = ['user_id', 'name', 'age']
        table_id = ['user_id']


def test_basemodel_dict_record():
    site = Site(name='site1', base_url='http://example-site1.com')
    assert 'name' in site.dict_record
    assert 'base_url' in site.dict_record

def test_dump_inserts_record():
    site = Site(name='site1', base_url='http://example-site1.com')
    pk = site.dump()

    assert isinstance(pk, list)
    assert len(pk) == 1

    # Validate insert into database
    selected_record = site.db().select_record_by_id(site.table_name, pk[0])

    assert selected_record['name'] == 'site1'
    assert selected_record['base_url'] == 'http://example-site1.com'

def test_dict_record_filters_private_fields():
    site = Site(name='site1', base_url='http://example-site1.com')
    site._internal = 'Secret'

    record = site.dict_record
    assert 'name' in record
    assert 'base_url' in record
    assert '_internal' not in record

def test_basemodel_from_id_in_database():
    site = Site(name='site1', base_url='http://example-site1.com')
    id=site.dump()

    site_from_db = site.from_id_in_database(id)
    assert isinstance(site_from_db, Site)

    assert site_from_db.name == 'site1'
    assert site_from_db.base_url == 'http://example-site1.com'


def test_basemodel_instance_from_parser_instance():
    class SiteParser:
        def __init__(self):
            self.name = 'siteB'
            self.base_url = 'http://example-siteB.com'
            self._internal = 'Secret'
            self.other_attribute = 'other'

    site_parser = SiteParser()
    site = Site.from_parser(site_parser)
    assert isinstance(site, Site)
    assert site.name == 'siteB'
    assert site.base_url == 'http://example-siteB.com'
    assert getattr(site, '_internal', None) is None
    assert getattr(site, 'other_attribute', None) is None