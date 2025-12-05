from models_for_test import SiteTest
import pytest
from src.orm.base import BaseORMModel
import datetime
from datetime import datetime, timedelta

def test_pk_property_returns_none_on_not_dumped_instances():
    site = SiteTest(name='site1', base_url='http://example-site1.com')
    assert isinstance(site.pk, list)
    assert len(site.pk) == 1
    assert site.pk[0] is None


def test_pk_property_returns_valid_pk_on_dumped_instances():
    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    site2 = SiteTest(name='site2', base_url='http://example-site2.com')
    pk1 = site1.dump()
    pk2 = site2.dump()

    assert isinstance(site1.pk, list)
    assert len(site1.pk) == 1

    assert site1.pk[0] == pk1[0]
    assert site2.pk[0] == pk2[0]


def test_init_raises_valueerror_for_invalid_columns():
    with pytest.raises(ValueError):
        site = SiteTest(name='site1', base_url='http://example-site1.com', invalid_col="invalid")

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
    site = SiteTest(name='site1', base_url='http://example-site1.com')
    assert 'name' in site.dict_record
    assert 'base_url' in site.dict_record

def test_basemodel_dict_record_ignores_columns():
    site = SiteTest(name='site1', base_url='http://example-site1.com')
    assert 'update_at' not in site.dict_record
    assert 'created_at' not in site.dict_record

def test_dump_inserts_record():
    site = SiteTest(name='site1', base_url='http://example-site1.com')
    pk = site.dump()

    assert isinstance(pk, list)
    assert len(pk) == 1

    # Validate insert into database
    selected_record = site.db().select_record_by_id(site.table_name, pk[0])

    assert selected_record['name'] == 'site1'
    assert selected_record['base_url'] == 'http://example-site1.com'


def test_dump_assign_pk():
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()
    site = SiteTest(name='site1', base_url='http://example-site1.com')
    pk = site.dump()

    assert site.site_id == pk[0]


def test_dump_method_includes_created_at_value():
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site = SiteTest(name='site1', base_url='http://example-site1.com')
    pk = site.dump()
    site_from_db = site.from_id_in_database(pk)
    assert site.created_at == site_from_db.created_at


def test_basemodel_dumped_to_db_property_changes_after_dump(db_instance):
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site = SiteTest(name='site1', base_url='http://example-site1.com')
    assert site.is_dumped == False
    site.dump()
    assert site.is_dumped == True

def test_update_method_updates_record_in_database():
    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    pk = site1.dump()

    site1_from_db = SiteTest.from_id_in_database(pk)
    assert site1_from_db.name == "site1"

    site1.name = "site1-new-name"
    site1.base_url = "http://example-site1-new-url.com"
    site1.update()
    site1_updated_from_db = SiteTest.from_id_in_database(pk)
    assert site1_updated_from_db.name == "site1-new-name"
    assert site1_updated_from_db.base_url == "http://example-site1-new-url.com"


def test_update_method_updates_specific_columns_for_record_in_database():
    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    pk = site1.dump()

    site1.name = "site1-new-name"
    site1.update()
    site1_from_db = SiteTest.from_id_in_database(pk)
    assert site1_from_db.pk == pk
    assert site1_from_db.name == "site1-new-name"
    assert site1_from_db.base_url == "http://example-site1.com"


def test_update_method_updates_updated_at_columns_for_record_in_database():
    created_at = datetime.now()
    created_at = created_at - timedelta(days=1)

    site1 = SiteTest(name='site1', base_url='http://example-site1.com', created_at=created_at)
    pk = site1.dump()
    assert site1.updated_at is None

    site1.update()
    site1_updated_from_db = SiteTest.from_id_in_database(pk)

    assert site1.updated_at == site1_updated_from_db.updated_at
    assert site1_updated_from_db.updated_at is not None
    assert isinstance(site1_updated_from_db.created_at, datetime)


def test_record_exists_detects_existing_record(db_instance):
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    site2 = SiteTest(name='site2', base_url='http://example-site2.com')
    site2_duplicated = SiteTest(name='site2', base_url='http://example-site2.com')

    assert site1.record_exists == False
    assert site2.record_exists == False

    site2.dump()
    assert site2.record_exists == True
    assert site2_duplicated.record_exists == True
    assert site1.record_exists == False


def test_record_exists_ignores_update_and_created_at_columns(db_instance):
    ...


def test_from_id_in_database_marks_instance_as_dumped(db_instance):
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    pk1 = site1.dump()
    site1_from_db = SiteTest.from_id_in_database(pk1)

    assert site1.is_dumped == True
    assert site1_from_db.is_dumped == True


def test_dump_avoids_duplicate_records():
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    site1_duplicated = SiteTest(name='site1', base_url='http://example-site1.com')

    pk1 = site1.dump()
    pk2 = site1_duplicated.dump()
    assert pk1 == pk2

    all_sites = SiteTest.all()
    assert len(all_sites) == 1

def test_dump_force_true_forces_duplicate_records():
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site1 = SiteTest(name='site1', base_url='http://example-site1.com')
    site2 = SiteTest(name='site1', base_url='http://example-site1.com')

    pk1 = site1.dump()
    pk2 = site2.dump(force=True)

    all_sites = SiteTest.all()
    assert len(all_sites) == 2

    SiteTest._db_object.rollback()


def test_dict_record_filters_private_fields():
    site = SiteTest(name='site1', base_url='http://example-site1.com')
    site._internal = 'Secret'

    record = site.dict_record
    assert 'name' in record
    assert 'base_url' in record
    assert '_internal' not in record

def test_basemodel_from_id_in_database():
    with SiteTest._db_object.connection.cursor() as cursor:
        cursor.execute("DELETE FROM sites;")
    SiteTest._db_object.connection.commit()

    site = SiteTest(name='site1', base_url='http://example-site1.com')
    id=site.dump()

    site_from_db = site.from_id_in_database(id)
    assert isinstance(site_from_db, SiteTest)

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
    site = SiteTest.from_parser(site_parser)
    assert isinstance(site, SiteTest)
    assert site.name == 'siteB'
    assert site.base_url == 'http://example-siteB.com'
    assert getattr(site, '_internal', None) is None
    assert getattr(site, 'other_attribute', None) is None