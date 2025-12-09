from src.orm.ORMModels import Site, Brand, Model, Version, VersionDetails


def test_ormmodel_db_returns_singleton():
    site1 = Site(name='Kavak', base_url='https://www.kava.com')
    site2 = Site(name='soloautos', base_url='https://www.soloautos.com')
    assert site1.db() is site2.db()