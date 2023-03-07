import psycopg2
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):

        db_settings = settings.DATABASES['default']

        with psycopg2.connect(
            host=db_settings['HOST'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            dbname=db_settings['NAME'],
            port=db_settings['PORT']
        ) as connection:
            with connection.cursor() as cursor:
                observation_table = """
                    CREATE TABLE sites_observation (
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
                        CONSTRAINT observation_datastream_id_fkey FOREIGN KEY (datastream_id) REFERENCES public.sites_datastream(id)
                    );
                """

                cursor.execute(observation_table)
                cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                cursor.execute("SELECT create_hypertable('sites_observation', 'result_time');")
