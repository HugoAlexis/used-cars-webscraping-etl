from src.orm.ORMModels import Site


def test_ormmodel_db_returns_singleton():
    site1 = Site(name='Kavak', base_url='https://www.kava.com')
    site2 = Site(name='soloautos', base_url='https://www.soloautos.com')
    assert site1.db() is site2.db()


def test_site_model_initialization():
    site = Site('Kavak', 'https://www.kavak.com')
    pk = site.dump()
    site_from_db = Site.from_id_in_database(pk)
    assert isinstance(site_from_db, Site)
    assert site_from_db.name == 'Kavak'
    assert site_from_db.base_url == 'https://www.kavak.com'
    print(site_from_db.site_id)