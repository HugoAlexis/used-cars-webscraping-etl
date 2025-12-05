from src.orm.ORMModels import Site


def test_site_model_initialization(db_instance):
    Site._db_object = db_instance
    site = Site('Kavak', 'https://www.kavak.com')

    pk = site.dump()
    site_from_db = Site.from_id_in_database(pk)
    assert isinstance(site_from_db, Site)
    assert site_from_db.name == 'Kavak'
    assert site_from_db.base_url == 'https://www.kavak.com'
    print(site_from_db.site_id)