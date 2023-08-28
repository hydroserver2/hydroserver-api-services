import psycopg2
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-timescale',
            action='store_true',
            help='Create the observations table without installing TimescaleDB or creating a hypertable.'
        )

    def handle(self, *args, **options):

        db_settings = settings.DATABASES['default']

        with psycopg2.connect(
            host=db_settings['HOST'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            dbname=db_settings['NAME'],
            port=db_settings['PORT'],
            connect_timeout=3
        ) as connection:
            with connection.cursor() as cursor:
                observation_table = """
                    CREATE TABLE IF NOT EXISTS Observation (
                        id uuid NOT NULL,
                        datastream_id uuid NOT NULL,
                        "result" float8 NOT NULL,
                        result_time timestamp NOT NULL,
                        result_quality varchar(255) NULL,
                        phenomenon_time timestamp NULL,
	                    valid_begin_time timestamp NULL,
	                    valid_end_time timestamp NULL,
                        CONSTRAINT "_datastream_uuid_phenomenon_time_uc" UNIQUE (datastream_id, result_time),
                        CONSTRAINT observation_pkey PRIMARY KEY (id, datastream_id, result_time),
                        CONSTRAINT observation_datastream_id_fkey FOREIGN KEY (datastream_id) REFERENCES public.Datastream(id)
                    );
                """

                cursor.execute(observation_table)

                if options['no_timescale'] is False:
                    cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                    cursor.execute("SELECT create_hypertable('Observation', 'result_time', if_not_exists => TRUE);")
