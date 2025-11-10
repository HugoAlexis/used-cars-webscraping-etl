# Used Cars Web Scraper & Market Analysis

This project is a production-oriented web scraping system built to collect, track, and analyze used car listings from multiple classified websites.
It was designed to demonstrate real-world data acquisition, parsing, database design, and engineering practices — suitable for freelance / commercial use cases.

## Objective

* Monitor used car markets daily
* Track how long each listing remains active before being sold
* Analyze pricing evolution, discounts, and site-to-site differences
* Build a structured dataset ready for analytics / ML / BI

## key Features
| Feature                               | Status |
| ------------------------------------- | ------ |
| Multi-site web scraping               | ✅      |
| Pagination iterators per website      | ✅      |
| Per-car parser model classes          | ✅      |
| Custom lightweight ORM using psycopg2 | ✅      |
| PostgreSQL storage                    | ✅      |
| Logging                               | ✅      |
| Unit tests                            | ✅      |
| Daily scheduled execution             | ✅      |

## Architecture Overview

used_cars_scraper/
│
├── used_cars/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py          # conexión y mini ORM
│   ├── models/              # los parsers (tu "dominio")
│   │   ├── __init__.py
│   │   ├── base.py          # clase base de parser
│   │   ├── sitioA.py        # parser sitio 1
│   │   ├── sitioB.py        # parser sitio 2
│   │   └── sitioC.py        # parser sitio 3 ...
│   ├── scrapers/            # iteradores/paginación
│   │   ├── base.py          # clase base scraper
│   │   ├── sitioA.py
│   │   ├── sitioB.py
│   │   └── sitioC.py
│   ├── scheduler/
│   │   ├── daily.py         # tareas diarias (ejecutar scraping)
│   │   └── airflow/cron/etc
│   ├── logging_config.py
│   └── utils.py
│
├── tests/
│   ├── test_models.py
│   ├── test_scrapers.py
│   ├── test_database.py
│   └── fixtures/
│
├── scripts/
│   ├── init_db.py
│   ├── run_daily_scrape.py  # esto se ejecuta via cron o systemd timer
│
├── requirements.txt
├── README.md
└── .env.example


## Tech Stack

| Area         | Tech                             |
| ------------ | -------------------------------- |
| Web Scraping | httpx / BeautifulSoup            |
| Database     | PostgreSQL                       |
| ORM          | custom minimal ORM (psycopg2)    |
| Scheduling   | cron / systemd / GitHub Actions  |
| Testing      | pytest                           |
| Logging      | Python `logging` standard module |


## Running

1. Install PostgreSQL locally
2. Create DB manually once (example: createdb used_cars)
3. First run will bootstrap schema automatically
4. Data collector can then be scheduled to run daily