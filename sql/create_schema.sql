CREATE TABLE "Sites"(
    "site_id" SERIAL NOT NULL,
    "name" VARCHAR(30) NOT NULL,
    "base_url" VARCHAR(120) NOT NULL
);
ALTER TABLE
    "Sites" ADD PRIMARY KEY("site_id");
CREATE TABLE "Cars"(
    "car_id" SERIAL NOT NULL,
    "site_id" INTEGER NOT NULL,
    "listing_id" VARCHAR(50) NOT NULL,
    "url" TEXT NOT NULL,
    "version_id" BIGINT NOT NULL,
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "updated_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "Cars" ADD PRIMARY KEY("car_id");
CREATE TABLE "Versions"(
    "version_id" SERIAL NOT NULL,
    "make" VARCHAR(50) NOT NULL,
    "model_name" VARCHAR(75) NOT NULL,
    "version_name" VARCHAR(75) NOT NULL,
    "year_prod" SMALLINT NOT NULL,
    "body_style" BIGINT NOT NULL,
    "engine_displacement" DECIMAL(3, 1) NOT NULL,
    "transmission_type" VARCHAR(30) NOT NULL,
    "created_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "updated_at" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL
);
ALTER TABLE
    "Versions" ADD PRIMARY KEY("version_id");
CREATE TABLE "Version_details"(
    "version_id" INTEGER NOT NULL,
    "mileage" DECIMAL(4, 1) NOT NULL,
    "cylinders" SMALLINT NOT NULL,
    "num_of_gears" SMALLINT NOT NULL,
    "fuel_range" SMALLINT NOT NULL,
    "engine_type" VARCHAR(255) NOT NULL,
    "fuel_type" VARCHAR(25) NOT NULL,
    "horsepower" SMALLINT NOT NULL,
    "rim_inches" SMALLINT NOT NULL,
    "rim_material" BIGINT NOT NULL,
    "num_of_doors" SMALLINT NOT NULL,
    "num_of_passengers" SMALLINT NOT NULL,
    "num_of_airbags" SMALLINT NOT NULL,
    "has_abs" BOOLEAN NOT NULL,
    "interior_materials" VARCHAR(30) NOT NULL,
    "has_start_button" BOOLEAN NOT NULL,
    "has_cruise_control" BOOLEAN NOT NULL,
    "has_distance_sensor" BOOLEAN NOT NULL,
    "has_bluetooth" BOOLEAN NOT NULL,
    "has_rain_sensor" BOOLEAN NOT NULL,
    "has_automatic_emergency_breaking" BOOLEAN NOT NULL,
    "has_gps" BOOLEAN NOT NULL,
    "has_sunroof" BOOLEAN NOT NULL,
    "has_androidauto" BOOLEAN NOT NULL,
    "has_applecarplay" BOOLEAN NOT NULL,
    "length_meters" BIGINT NOT NULL,
    "height_meters" DECIMAL(4, 2) NOT NULL,
    "width_meters" DECIMAL(4, 2) NOT NULL,
    "weight_kg" SMALLINT NOT NULL
);
ALTER TABLE
    "Version_details" ADD PRIMARY KEY("version_id");
CREATE TABLE "car_info"(
    "car_id" BIGINT NOT NULL,
    "city" VARCHAR(100) NOT NULL,
    "odometer" INTEGER NOT NULL,
    "image_path" TEXT NOT NULL,
    "report_path" TEXT NOT NULL
);
ALTER TABLE
    "car_info" ADD PRIMARY KEY("car_id");
CREATE TABLE "report_conditions"(
    "car_id" BIGINT NOT NULL,
    "inspection_date" DATE NOT NULL,
    "tire_condition" SMALLINT NOT NULL,
    "break_pads_condition" SMALLINT NOT NULL,
    "engine_oil_condition" SMALLINT NOT NULL,
    "air_filter_condition" SMALLINT NOT NULL,
    "theft_report" BOOLEAN NOT NULL,
    "debts" INTEGER NOT NULL,
    "vin_number" BIGINT NOT NULL
);
ALTER TABLE
    "report_conditions" ADD PRIMARY KEY("car_id");
CREATE TABLE "scrapes"(
    "scrape_id" SERIAL NOT NULL,
    "timestamp_start" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "timestamp_end" TIMESTAMP(0) WITHOUT TIME ZONE NOT NULL,
    "finish_ok" BOOLEAN NOT NULL,
    "error_type" VARCHAR(40) NOT NULL,
    "error_msg" TEXT NOT NULL
);
ALTER TABLE
    "scrapes" ADD PRIMARY KEY("scrape_id");
CREATE TABLE "car_snapshots"(
    "scrape_id" INTEGER NOT NULL,
    "car_id" INTEGER NOT NULL,
    "labels" TEXT NOT NULL,
    "price" BIGINT NOT NULL
);
ALTER TABLE
    "car_snapshots" ADD CONSTRAINT "car_snapshots_scrape_id_unique" UNIQUE("scrape_id");
ALTER TABLE
    "car_snapshots" ADD CONSTRAINT "car_snapshots_car_id_unique" UNIQUE("car_id");
ALTER TABLE
    "car_snapshots" ADD CONSTRAINT "car_snapshots_car_id_foreign" FOREIGN KEY("car_id") REFERENCES "Cars"("car_id");
ALTER TABLE
    "Version_details" ADD CONSTRAINT "version_details_version_id_foreign" FOREIGN KEY("version_id") REFERENCES "Versions"("version_id");
ALTER TABLE
    "car_snapshots" ADD CONSTRAINT "car_snapshots_scrape_id_foreign" FOREIGN KEY("scrape_id") REFERENCES "scrapes"("scrape_id");
ALTER TABLE
    "report_conditions" ADD CONSTRAINT "report_conditions_car_id_foreign" FOREIGN KEY("car_id") REFERENCES "car_info"("car_id");
ALTER TABLE
    "Cars" ADD CONSTRAINT "cars_version_id_foreign" FOREIGN KEY("version_id") REFERENCES "Versions"("version_id");
ALTER TABLE
    "Cars" ADD CONSTRAINT "cars_car_id_foreign" FOREIGN KEY("car_id") REFERENCES "car_info"("car_id");
ALTER TABLE
    "Sites" ADD CONSTRAINT "sites_site_id_foreign" FOREIGN KEY("site_id") REFERENCES "Cars"("car_id");