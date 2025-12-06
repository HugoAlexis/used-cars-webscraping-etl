from ..orm.base import BaseORMModel
from datetime import datetime
import os

class Site(BaseORMModel):
    table_name = 'sites'
    table_columns = ['site_id', 'name', 'base_url', 'updated_at', 'created_at']
    table_id = ['site_id']

    def __init__(self, name, base_url, **kwargs):
        super().__init__(name=name, base_url=base_url, **kwargs)


class Brand(BaseORMModel):
    table_name = 'brands'
    table_columns = ['brand_id', 'brand_name', 'country_iso', 'founded_year',
                     'website_url', 'updated_at', 'created_at']
    table_id = ['brand_id']

    def __init__(self, brand_name, country_iso, founded_year, website_url, **kwargs):
        super().__init__(
            brand_name=brand_name,
            country_ido=country_iso,
            founded_year=founded_year,
            website_url=website_url,
            **kwargs
        )


class Model(BaseORMModel):
    table_name = 'models'
    table_columns = [
        'model_id',
        'brand_id',            # References Brand (brand_id)
        'model_name',
        'created_at',
        'updated_at',
    ]
    table_id = ['model_id']
    def __init__(self, brand_id, model_name, **kwargs):
        super().__init__(
            brand_id = brand_id,
            model_name=model_name,
            **kwargs
        )


class Version(BaseORMModel):
    table_name = 'versions'
    table_columns = [
        'version_id',
        'model_id',            # References Model (model_id)
        'version_name',
        'year_prod',
        'body_style',
        'engine_displacement',
        'transmission_type',
        'created_at',
        'updated_at',
    ]
    table_id = ['version_id']

    def __init__(self, model_id, version_name, year_prod, body_style, engine_displacement,transmission_type, **kwargs):
        super().__init__(
            model_id=model_id,
            version_name=version_name,
            year_prod=year_prod,
            body_style=body_style,
            engine_displacement=engine_displacement,
            transmission_type=transmission_type,
            **kwargs
        )


class VersionDetails(BaseORMModel):
    table_name = 'version_details'
    table_columns = [
        'version_id',
        'engine_type',
        'fuel_type',
        'mileage',
        'cylinders',
        'drivetrain',
        'num_of_gears',
        'fuel_range',
        'horsepower',
        'acceleration_0to100_kph',
        'rim_inches',
        'rim_material',
        'interior_material',
        'num_of_doors',
        'num_of_passengers',
        'num_of_airbags',
        'has_abs',
        'has_start_button',
        'has_cruise_control',
        'has_distance_sensor',
        'has_bluetooth',
        'has_rain_sensor',
        'has_automatic_emergency_breaking',
        'has_gps',
        'has_touchscreen',
        'has_sunroof',
        'has_androidauto',
        'has_applecarplay',
        'length_meters',
        'height_meters',
        'width_meters',
        'weight_kg',
        'created_at',
        'updated_at',
    ]


class Scrape(BaseORMModel):
    table_name = 'scrapes'
    table_columns = ['scrape_id', 'timestamp_start', 'timestamp_end', 'finish_ok', 'error_type',
                     'error_msg', 'listings_found', 'listings_saved']
    table_id = ['scrape_id']
    def __init__(self, **kwargs):
        super().__init__(
            timestamp_start=datetime.now(),
            timestamp_end=None,
            finish_ok=False,
            error_type=None,
            error_msg=None,
            listings_found=None,
            listings_saved=None,
            **kwargs
        )


class CarListing(BaseORMModel):
    table_name = 'car_listings'
    table_columns = ['car_id', 'site_id', 'listing_id', 'url', 'version_id', 'city', 'odometer',
                     'image_path', 'report_path', 'created_at', 'updated_at']
    table_id = ['car_id']
    def __init__(self, site_id, listing_id, url, version_id, city, odometer, **kwargs):
        super().__init__(
            site_id=site_id,
            listing_id=listing_id,
            url=url,
            version_id=version_id,
            city=city,
            odometer=odometer,
            image_path=os.path.join("data", "images", f"site_{site_id}", f"image_{listing_id}" ),
            report_path=os.path.join("data", "reports", f"site_{site_id}", f"image_{listing_id}.pdf" )
            **kwargs
        )


class ReportConditions(BaseORMModel):
    table_name = 'report_conditions'
    table_columns = [
        'car_id',                          # References CarListing.car_id
        'inspection_date',
        'tire_condition',
        'break_pads_condition',
        'engine_oil_condition',
        'air_filter_condition',
        'theft_report',
        'debts',
        'created_at',
        'updated_at',
    ]


class CarSnapshot(BaseORMModel):
    table_name = 'car_snapshots'
    table_columns = [
        'scrape_id',                        # References Scrape.scrape_id
        'car_id',                           # References CarListing.car_id
        'labels',
        'price'
    ]