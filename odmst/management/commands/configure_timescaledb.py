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
                    CREATE TABLE odmst_observation (
                        uuid uuid NOT NULL,
                        datastream_uuid uuid NOT NULL,
                        phenomenon_time timestamp NOT NULL,
                        "result" float8 NOT NULL,
                        result_quality varchar(255) NULL,
	                    valid_begin_time timestamp NULL,
	                    valid_end_time timestamp NULL,
                        CONSTRAINT "_datastream_uuid_phenomenon_time_uc" UNIQUE (datastream_uuid, phenomenon_time),
                        CONSTRAINT observation_pkey PRIMARY KEY (uuid, datastream_uuid, phenomenon_time),
                        CONSTRAINT observation_datastream_uuid_fkey FOREIGN KEY (datastream_uuid) REFERENCES public.odmst_datastream(uuid),
                        CONSTRAINT observation_result_quality_fkey FOREIGN KEY (result_quality) REFERENCES public.odmst_resultqualitycv("name")
                    );
                """

                cursor.execute(observation_table)
                cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                cursor.execute("SELECT create_hypertable('odmst_observation', 'phenomenon_time');")
