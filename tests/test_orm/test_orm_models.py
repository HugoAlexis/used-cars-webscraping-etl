import pytest
from src.orm.ORMModels import (
    Site, Brand, Model, Version, VersionDetails, Scrape, CarListing, ReportConditions, CarSnapshot
)
from datetime import datetime

@pytest.mark.parametrize(
    'ModelClass,init_kwargs',
    [
        (Site, {'name': 'Site1', 'base_url':'http://www.site1-shop.com'}),
        (Brand, {'brand_name':'Ford', 'country_iso':'USA', 'founded_year':1915, 'website_url':'www.ford-company.com'}),
        (Model, {'brand_id':1, 'model_name':'Civic'}),
        (Version, {'model_id': 1, 'version_name': 'LX', 'year_prod': 2009, 'body_style': 'COUPE',
                   'engine_displacement':2.5, 'transmission_type':'Automatic'}),
        (VersionDetails, {'engine_type':'electric', 'fuel_type': 'electricity', 'mileage': 5.6, 'cylinders': 3,
                          'drivetrain':'4x4', 'num_of_gears':7, 'fuel_range': 650, 'horsepower': 180,
                          'acceleration_0to100_kph': 7.8, 'rim_inches': 18, 'rim_material': 'aluminium',
                          'interior_material': 'leather', 'num_of_doors': 5, 'num_of_passengers': 5, 'num_of_airbags': 5,
                          'has_abs': True, 'has_start_button': True, 'has_cruise_control': True,
                          'has_distance_sensor': True, 'has_bluetooth': True, 'has_automatic_emergency_breaking': False,
                          'has_gps': True, 'has_touchscreen': True, 'has_sunroof': False, 'has_androidauto': False,
                          'has_applecarplay': True, 'length_meters': 4.1, 'height_meters': 1.53, 'width_meters': 2.12,
                          'weight_kg': 1743}),
        (Scrape, {}),
        (CarListing, {'site_id':3, 'listing_id':'K23454L', 'url':'https://www.site1-market.com/k23454L',
                      'version_id':2, 'city':'CMDX', 'odometer':98563}),

        (ReportConditions, {'car_id':3, 'inspection_date':'2025-08-19', 'tire_condition':98, 'break_pads_condition':34,
                            'engine_oil_condition':54, 'air_filter_condition':85, 'theft_report':False, 'debts': 0}),
    ]
)
def test_model_initialization(ModelClass, init_kwargs):
    obj = ModelClass(**init_kwargs)
    for col in obj.table_columns:
        if col in init_kwargs:
            assert getattr(obj, col) == init_kwargs[col]
        if 'created_at' in obj.table_columns:
            created_at = getattr(obj, 'created_at', None)
            assert isinstance(created_at, datetime)
            assert created_at is not None
        if 'updated_at' in obj.table_columns:
            assert getattr(obj, 'updated_at', None) is None   # For new records (non existing in DB), updated at is None
