# HydroServer Webapp Backend

CIROH Hydrologic Information System is a web application built with Django that allows users to view and analyze 
hydrologic data. The application uses TimescaleDB, an open-source time-series database, to store and manage large 
amounts of hydrologic data.

## Setting up the Development Environment

### Prerequisites

Before starting, make sure you have the following software installed on your machine:
- Python 3.10+
- Docker

### Clone the Repository

Clone the CIROH Hydrologic Information System repository from GitHub:

```bash
git clone https://github.com/hydroserver2/hydroserver.git
cd hydroserver
```

### Install Dependencies

Install the Python dependencies using pip:

```bash
pip install -r requirements.txt
```

### Run TimescaleDB in Docker

CIROH Hydrologic Information System requires a TimescaleDB instance to store data. We will use Docker to run 
TimescaleDB:

```bash
docker run -d --name timescaledb -p 5432:5432 -e POSTGRES_PASSWORD=password -e POSTGRES_DB=tsdb timescale/timescaledb-ha:pg14-latest
```

### Define Django Settings

Django settings can be assigned to environment variables or entered into a `.env` file. For
a basic development environment, only `DATABASE_URL` needs to be defined.

1. Create a `.env` file in your project directory.
2. In `.env`, assign your local TimescaleDB connection URL to `DATABASE_URL`. If you followed the instructions in the previous step to set up TimescaleDB, the connection URL should be `postgresql://postgres:password@localhost:5432/tsdb`

### Run Django Migrations

Run Django migrations to create necessary database tables with the following command:

```bash
python manage.py migrate
```

### Setup TimescaleDB Tables

TimescaleDB installation and hypertables require additional steps beyond the Django migrate command. Run the following
command to create the observations table, install TimescaleDB, and set up the observation table as a hypertable.

```bash
python manage.py configure_timescaledb
```

If you aren't using the TimescaleDB extension in development, instead run the following command to create the
observations table without installing TimescaleDB or setting up a hypertable.

```bash
python manage.py configure_timescaledb --no-timescale
```

### Collect Static Files

Run the following command to collect Django static files:

```bash
python manage.py collectstatic
```

### Load Test Data
CIROH Hydrologic Information System comes with some sample data that you can load into the database:

```bash
python manage.py loaddata test_data.yaml
```

### Start the Development Web Server
Start the development web server:

```bash
python manage.py runserver
```

### Access the Web Application
You can now access CIROH Hydrologic Information System at http://localhost:8000 in your web browser.

## Contributing

If you'd like to contribute to CIROH Hydrologic Information System, please follow these steps:
1. Fork the repository
2. Create a new branch (git checkout -b my-new-feature)
3. Make changes and commit (git commit -am 'Add some feature')
4. Push to the branch (git push origin my-new-feature)
5. Create a pull request

## Funding and Acknowledgements

Funding for this project was provided by the National Oceanic & Atmospheric Administration (NOAA), awarded to the Cooperative Institute for Research to Operations in Hydrology (CIROH) through the NOAA Cooperative Agreement with The University of Alabama (NA22NWS4320003).
