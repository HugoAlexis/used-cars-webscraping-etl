CREATE TABLE Sites(
    site_id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    base_url VARCHAR(90) NOT NULL
);

CREATE TABLE Versions(
    version_id SERIAL PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model_name VARCHAR(75) NOT NULL,
    version_name VARCHAR(75) NOT NULL,
    year_prod SMALLINT NOT NULL,
    body_style BIGINT NOT NULL,
    engine_displacement DECIMAL(3, 1) NOT NULL,
    transmission_type VARCHAR(30) NOT NULL,
    created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE Cars(
    car_id SERIAL PRIMARY KEY,
    site_id INTEGER NOT NULL REFERENCES Sites(site_id),
    listing_id VARCHAR(50) NOT NULL,
    url TEXT NOT NULL,
    version_id BIGINT NOT NULL REFERENCES Versions (version_id),
    created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE version_details(
    version_id INTEGER REFERENCES Versions(version_id),
    mileage DECIMAL(4, 1),
    cylinders SMALLINT,
    num_of_gears SMALLINT,
    fuel_range SMALLINT,
    engine_type VARCHAR(255),
    fuel_type VARCHAR(25),
    horsepower SMALLINT,
    rin_inches SMALLINT,
    rin_material BIGINT,
    num_of_doors SMALLINT,
    num_of_passengers SMALLINT,
    num_of_airbats SMALLINT,
    has_abs BOOLEAN,
    interior_materials VARCHAR(30),
    has_start_button BOOLEAN,
    has_cruise_control BOOLEAN,
    has_distance_sensor BOOLEAN,
    has_bluetooth BOOLEAN,
    has_rain_sensor BOOLEAN,
    has_automatic_emergency_breaking BOOLEAN,
    has_gps BOOLEAN,
    has_sunroof BOOLEAN,
    has_androidauto BOOLEAN,
    has_applecarplay BOOLEAN,
    length_meters BIGINT,
    height_meters DECIMAL(4, 2),
    width_meters DECIMAL(4, 2),
    weight_kg SMALLINT,
    created_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    updated_at TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);

CREATE TABLE car_info(
    car_id INTEGER REFERENCES Cars(car_id),
    city VARCHAR(100),
    odometer INTEGER,
    image_path TEXT NOT NULL,
    report_path TEXT NOT NULL
);

CREATE TABLE report_conditions(
    car_id BIGINT REFERENCES Cars(car_id),
    inspection_date DATE,
    tire_condition SMALLINT,
    break_pads_condition SMALLINT,
    engine_oil_condition SMALLINT,
    air_filter_condition SMALLINT,
    theft_report BOOLEAN,
    debts INTEGER,
    vin_number VARCHAR(50)
);

CREATE TABLE Scrapes(
    scrape_id SERIAL PRIMARY KEY,
    timestamp_start TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    timestamp_end TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    finish_ok BOOLEAN NOT NULL DEFAULT FALSE,
    error_type VARCHAR(40),
    error_message TEXT
);

CREATE TABLE Car_snapshots(
    scrape_id INTEGER NOT NULL REFERENCES Scrapes (scrape_id),
    car_id INTEGER NOT NULL REFERENCES Cars (car_id),
    labels TEXT,
    price BIGINT
);