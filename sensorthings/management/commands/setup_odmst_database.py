from sqlalchemy import create_engine, text
from django.core.management.base import BaseCommand
from odmst.sa_models import Base


class Command(BaseCommand):

    def handle(self, *args, **options):

        engine = create_engine('postgresql+psycopg2://postgres:password@localhost:5432/hydroserver')

        Base.metadata.create_all(engine)

        with engine.connect() as connection:
            connection.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb;"))
            connection.execute(text("SELECT create_hypertable('observation', 'phenomenon_time');"))
