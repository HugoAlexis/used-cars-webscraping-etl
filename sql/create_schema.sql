DROP TABLE IF EXISTS report_conditions;
DROP TABLE IF EXISTS car_snapshots;
DROP TABLE IF EXISTS car_listings;
DROP TABLE IF EXISTS scrapes;
DROP TABLE IF EXISTS sites;
DROP TABLE IF EXISTS version_details;
DROP TABLE IF EXISTS versions;
DROP TABLE IF EXISTS models;
DROP TABLE IF EXISTS brands;

CREATE TABLE sites (
    site_id SMALLSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    base_url VARCHAR(120) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);


CREATE TABLE brands (
    brand_id SMALLSERIAL PRIMARY KEY,
    brand_name VARCHAR(50) UNIQUE NOT NULL,
    country_iso CHAR(3),
    founded_year SMALLINT,
    website_url VARCHAR(200),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);


CREATE TABLE models (
    model_id SMALLSERIAL PRIMARY KEY,
    brand_id SMALLINT REFERENCES brands (brand_id) ON DELETE RESTRICT NOT NULL,
    model_name VARCHAR(75) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	CONSTRAINT unique_brand_model UNIQUE (brand_id, model_name)
);


CREATE TABLE versions (
    version_id SMALLSERIAL PRIMARY KEY,
    model_id SMALLINT REFERENCES models (model_id) ON DELETE RESTRICT  NOT NULL,
    version_name VARCHAR(75) NOT NULL,
    year_prod SMALLINT NOT NULL,
    body_style VARCHAR(50),
    engine_displacement DECIMAL(3,1),
    transmission_type VARCHAR(30),
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	CONSTRAINT prod_year_valid CHECK (year_prod BETWEEN 1885 AND EXTRACT(YEAR FROM NOW())),
    CONSTRAINT unique_combination UNIQUE (model_id, version_name, year_prod, engine_displacement, transmission_type)
);

CREATE TABLE version_details (
    version_id SMALLINT PRIMARY KEY REFERENCES versions (version_id) ON DELETE CASCADE,
    engine_type VARCHAR(50),
    fuel_type VARCHAR(50),
    mileage INT,
    cylinders SMALLINT,
    drivetrain VARCHAR(15),
    num_of_gears SMALLINT,
    fuel_range SMALLINT,
    horsepower SMALLINT,
    acceleration_0to100_kph DECIMAL(3,1),
    rim_inches SMALLINT,
    rim_material VARCHAR(35),
    interior_material VARCHAR(35),
    num_of_doors SMALLINT,
    num_of_passengers SMALLINT,
    num_of_airbags SMALLINT,
    has_abs BOOLEAN,
    has_start_button BOOLEAN,
    has_cruise_control BOOLEAN,
    has_distance_sensor BOOLEAN,
    has_bluetooth BOOLEAN,
    has_rain_sensor BOOLEAN,
    has_automatic_emergency_breaking BOOLEAN,
    has_gps BOOLEAN,
    has_touchscreen BOOLEAN,
    has_sunroof BOOLEAN,
    has_androidauto BOOLEAN,
    has_applecarplay BOOLEAN,
    length_meters DECIMAL(5,2),
    height_meters DECIMAL(5,2),
    width_meters DECIMAL(5,2),
    weight_kg SMALLINT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
);


CREATE TABLE scrapes (
    scrape_id SMALLSERIAL PRIMARY KEY,
    timestamp_start TIMESTAMP DEFAULT NOW() NOT NULL,
    timestamp_end TIMESTAMP,
    finish_ok BOOLEAN NOT NULL DEFAULT FALSE,
    error_type VARCHAR(50),
    error_msg TEXT,
    listings_found INTEGER,
    listings_saved INTEGER
);


CREATE TABLE car_listings (
    car_id SERIAL PRIMARY KEY,
    site_id SMALLINT REFERENCES sites (site_id) ON DELETE RESTRICT NOT NULL,
    listing_id VARCHAR(150) NOT NULL,
    url TEXT NOT NULL,
    version_id SMALLINT REFERENCES versions (version_id) ON DELETE RESTRICT NOT NULL,
    city VARCHAR(120),
    odometer INTEGER,
    image_path TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	CONSTRAINT unique_site_listing UNIQUE (site_id, listing_id),
	CONSTRAINT odometer_valid CHECK (odometer >= 0)
);


CREATE TABLE report_conditions (
    car_id INT PRIMARY KEY REFERENCES car_listings (car_id) ON DELETE CASCADE,
    inspection_date DATE,
    tire_condition SMALLINT,         -- Percentage, when available
    break_pads_condition SMALLINT,   -- Percentage, when available
    engine_oil_condition SMALLINT,   -- Percentage, when available
    air_filter_condition SMALLINT,   -- Percentage, when available
    theft_report BOOLEAN,
    debts INT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
	CONSTRAINT pct_tire_condition CHECK (tire_condition BETWEEN 0 AND 100),
	CONSTRAINT pct_break_pads_condition CHECK (break_pads_condition BETWEEN 0 AND 100),
	CONSTRAINT pct_engine_oil_condition CHECK (engine_oil_condition BETWEEN 0 AND 100),
	CONSTRAINT pct_air_filter_condition CHECK (air_filter_condition BETWEEN 0 AND 100)
);


CREATE TABLE car_snapshots (
    scrape_id SMALLINT REFERENCES scrapes (scrape_id) ON DELETE CASCADE,
    car_id INT REFERENCES car_listings (car_id) ON DELETE CASCADE,
    labels TEXT,
    price INT,
	PRIMARY KEY (scrape_id, car_id)
);

-- Create indexes for quering Database
CREATE INDEX idx_car_listings_version_id ON car_listings (version_id);
CREATE INDEX idx_car_listings_site_listing ON car_listings (site_id, listing_id);
CREATE INDEX idx_snapshots_car ON car_snapshots (car_id);
CREATE INDEX idx_snapshots_scrape ON car_snapshots (scrape_id);
CREATE INDEX idx_listings_city ON car_listings (city);
CREATE INDEX idx_versions_model_year ON versions (model_id, year_prod);


-- Handle engine_displacement/transmission_type NULL values
CREATE UNIQUE INDEX idx_unique_version
ON versions (
    model_id,
    version_name,
    year_prod,
    COALESCE(engine_displacement, -1),
    COALESCE(transmission_type, '__UNKNOWN__')
);