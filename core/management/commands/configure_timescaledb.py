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

        parser.add_argument(
            '--partition-interval-days',
            default=7,
            help='Set the observations hypertable partition interval value in days.'
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
                    CREATE TABLE IF NOT EXISTS "Observation" (
                        "id" uuid NOT NULL,
                        "datastreamId" uuid NOT NULL,
                        "featureOfInterestId" uuid NULL,
                        "phenomenonTime" timestamp NOT NULL,
                        "result" float8 NOT NULL,
                        "resultTime" timestamp NULL,
                        "qualityCode" varchar(255) NULL,
                        "resultQualifiers" uuid[] NULL,
                        CONSTRAINT "_datastream_uuid_phenomenon_time_uc" UNIQUE ("datastreamId", "phenomenonTime"),
                        CONSTRAINT observation_pkey PRIMARY KEY ("id", "datastreamId", "phenomenonTime"),
                        CONSTRAINT observation_datastream_id_fkey FOREIGN KEY ("datastreamId") REFERENCES public."Datastream"(id),
                        CONSTRAINT observation_feature_of_interest_id_fkey FOREIGN KEY ("featureOfInterestId") REFERENCES public."Datastream"(id)
                    );
                """

                cursor.execute(observation_table)

                if options['no_timescale'] is False:
                    cursor.execute(
                        "CREATE EXTENSION IF NOT EXISTS timescaledb;"
                    )
                    cursor.execute(
                        f"SELECT create_hypertable("
                        f"'\"Observation\"', "
                        f"'phenomenonTime', "
                        f"chunk_time_interval => INTERVAL '{options['partition_interval_days']} day', "
                        f"if_not_exists => TRUE"
                        f");"
                    )
