import psycopg2
from django.core.management.base import BaseCommand
from django.conf import settings
from psycopg2 import OperationalError, Error


class Command(BaseCommand):
    help = "Create or update the Observation table and optionally set it as a TimescaleDB hypertable."

    def add_arguments(self, parser):
        parser.add_argument(
            '--setup-timescaledb',
            action='store_true',
            help='Create the observations table as a hypertable if using TimescaleDB.'
        )

        parser.add_argument(
            '--partition-interval-days',
            default=365,
            type=int,
            help='Set the observations hypertable partition interval value in days.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("\nChecking Observation table setup..."))
        db_settings = settings.DATABASES['default']

        try:
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
                            "phenomenonTime" timestamptz NOT NULL,
                            "result" float8 NOT NULL,
                            "resultTime" timestamptz NULL,
                            "qualityCode" varchar(255) NULL,
                            "resultQualifiers" uuid[] NULL,
                            CONSTRAINT "_datastream_uuid_phenomenon_time_uc" UNIQUE ("datastreamId", "phenomenonTime"),
                            CONSTRAINT observation_pkey PRIMARY KEY ("id", "datastreamId", "phenomenonTime"),
                            CONSTRAINT observation_datastream_id_fkey FOREIGN KEY ("datastreamId") REFERENCES public."Datastream"(id),
                            CONSTRAINT observation_feature_of_interest_id_fkey FOREIGN KEY ("featureOfInterestId") REFERENCES public."Datastream"(id)
                        );
                    """
                    cursor.execute(observation_table)

                    if options['setup_timescaledb']:
                        cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
                        cursor.execute(
                            f"SELECT create_hypertable("
                            f"'\"Observation\"', "
                            f"'phenomenonTime', "
                            f"chunk_time_interval => INTERVAL '{options['partition_interval_days']} day', "
                            f"if_not_exists => TRUE"
                            f");"
                        )

        except OperationalError as e:
            self.stdout.write(self.style.ERROR(f"Database connection failed: {e}"))
        except Error as e:
            self.stdout.write(self.style.ERROR(f"An error occurred while executing Observation table setup: {e}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"An unexpected error occurred setting up Observation table: {e}"))

        self.stdout.write(self.style.SUCCESS("Finished checking Observation table setup."))
