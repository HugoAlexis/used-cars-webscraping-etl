from keyword import kwlist

from ..orm.base import BaseORMModel
from datetime import datetime
import os


class Site(BaseORMModel):
    table_name = 'sites'
    table_columns = [
        'site_id',
        'name',
        'base_url',
        'updated_at',
        'created_at']
    table_id = ['site_id']

    def __init__(self,
                 name,
                 base_url,
                 **kwargs):
        super().__init__(name=name, base_url=base_url, **kwargs)



class Brand(BaseORMModel):
    table_name = 'brands'
    table_columns = ['brand_id',
                     'brand_name',
                     'country_iso',
                     'founded_year',
                     'website_url',
                     'updated_at',
                     'created_at']
    table_id = ['brand_id']

    def __init__(self,
                 brand_name,
                 country_iso=None,
                 founded_year=None,
                 website_url=None,
                 **kwargs):
        super().__init__(
            brand_name=brand_name,
            country_iso=country_iso,
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
    def __init__(self,
                 brand_id,
                 model_name,
                 **kwargs):
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

    def __init__(self,
                 model_id,
                 version_name,
                 year_prod,
                 body_style=None,
                 engine_displacement=None,
                 transmission_type=None,
                 **kwargs):
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
    def __init__(self,
                 engine_type=None,
                 fuel_type=None,
                 mileage=None,
                 cylinders=None,
                 drivetrain=None,
                 num_of_gears=None,
                 fuel_range=None,
                 horsepower=None,
                 acceleration_0to100_kph=None,
                 rim_inches=None,
                 rim_material=None,
                 interior_material=None,
                 num_of_doors=None,
                 num_of_passengers=None,
                 num_of_airbags=None,
                 has_abs=None,
                 has_start_button=None,
                 has_cruise_control=None,
                 has_distance_sensor=None,
                 has_bluetooth=None,
                 has_rain_sensor=None,
                 has_automatic_emergency_breaking=None,
                 has_gps=None,
                 has_touchscreen=None,
                 has_sunroof=None,
                 has_androidauto=None,
                 has_applecarplay=None,
                 length_meters=None,
                 width_meters=None,
                 weight_kg=None,
                 **kwargs
                 ):
        super().__init__(engine_type=engine_type,
                         fuel_type=fuel_type,
                         mileage=mileage,
                         cylinders=cylinders,
                         drivetrain=drivetrain,
                         num_of_gears=num_of_gears,
                         fuel_range=fuel_range,
                         horsepower=horsepower,
                         acceleration_0to100_kph=acceleration_0to100_kph,
                         rim_inches=rim_inches,
                         rim_material=rim_material,
                         interior_material= interior_material,
                         num_of_doors=num_of_doors,
                         num_of_passengers=num_of_passengers,
                         num_of_airbags=num_of_airbags,
                         has_abs=has_abs,
                         has_start_button=has_start_button,
                         has_cruise_control=has_cruise_control,
                         has_distance_sensor=has_distance_sensor,
                         has_bluetooth=has_bluetooth,
                         has_rain_sensor=has_rain_sensor,
                         has_automatic_emergency_breaking=has_automatic_emergency_breaking,
                         has_gps=has_gps,
                         has_touchscreen=has_touchscreen,
                         has_sunroof=has_sunroof,
                         has_androidauto=has_androidauto,
                         has_applecarplay=has_applecarplay,
                         length_meters=length_meters,
                         width_meters=width_meters,
                         weight_kg=weight_kg,
                         **kwargs)



class Scrape(BaseORMModel):
    table_name = 'scrapes'
    table_columns = [
        'scrape_id',
        'timestamp_start',
        'timestamp_end',
        'finish_ok',
        'error_type',
        'error_msg',
        'listings_found',
        'listings_saved'
    ]
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
    def __init__(self,
                 site_id,
                 listing_id,
                 url,
                 version_id,
                 city=None,
                 odometer=None,
                 **kwargs):
        super().__init__(
            site_id=site_id,
            listing_id=listing_id,
            url=url,
            version_id=version_id,
            city=city,
            odometer=odometer,
            image_path=os.path.join("data", "images", f"site_{site_id}", f"image_{listing_id}" ),
            report_path=os.path.join("data", "reports", f"site_{site_id}", f"image_{listing_id}" ),
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
    def __init__(self,
                 car_id,
                 inspection_date=None,
                 tire_condition=None,
                 break_pads_condition=None,
                 engine_oil_condition=None,
                 air_filter_condition=None,
                 theft_report=None,
                 debts=None,
                 **kwargs):
        super().__init__(
            car_id=car_id,
            inspection_date=inspection_date,
            tire_condition=tire_condition,
            break_pads_condition=break_pads_condition,
            engine_oil_condition=engine_oil_condition,
            air_filter_condition=air_filter_condition,
            theft_report=theft_report,
            debts=debts,
            **kwargs
        )



class CarSnapshot(BaseORMModel):
    table_name = 'car_snapshots'
    table_columns = [
        'scrape_id',                        # References Scrape.scrape_id
        'car_id',                           # References CarListing.car_id
        'labels',
        'price'
    ]
    def __init__(self,
                 scrape_id,
                 car_id,
                 labels=None,
                 price=None,
                 **kwargs):
        super().__init__(
            scrape_id=scrape_id,
            car_id=car_id,
            labels=labels,
            price=price,
            **kwargs
        )