DROP TABLE IF EXISTS table_1;
DROP TABLE IF EXISTS table_2;
DROP TABLE IF EXISTS joint_table1_table2;
DROP TABLE IF EXISTS sites_testing;

-- For Testing Database ONLY
CREATE TABLE table_1 (
	t1_id SERIAL PRIMARY KEY,
	name_t1 VARCHAR(25)
);

CREATE TABLE table_2 (
	t2_id SERIAL PRIMARY KEY,
	name_t2 VARCHAR(25)
);

CREATE TABLE joint_table1_table2 (
	t1_id INTEGER REFERENCES table_1 (t1_id),
	t2_id INTEGER REFERENCES table_2 (t2_id),
	PRIMARY KEY (t1_id, t2_id)
);

-- Sites testing without unique constraints. For Testing operations with duplicate records
CREATE TABLE sites_testing (
    site_id SMALLSERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    base_url VARCHAR(120) NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW() NOT NULL
)

