import psycopg2
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    def handle(self, *args, **options):
        """"""

        db_settings = settings.DATABASES['default']

        with psycopg2.connect(
            host=db_settings['HOST'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            dbname=db_settings['NAME'],
            port=db_settings['PORT']
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

                datastream_view = """
                
                """

                feature_of_interest_view = """
                    CREATE OR REPLACE VIEW "FEATURES" AS
                        SELECT NULL AS "ID",
                               NULL AS "NAME",
                               NULL AS "DESCRIPTION",
                               NULL AS "PROPERTIES",
                               NULL AS "ENCODING_TYPE",
                               NULL AS "FEATURE",
                               NULL AS "GEOM"
                        LIMIT 0
                """

                historical_location_view = """
                    CREATE OR REPLACE VIEW "HIST_LOCATIONS" AS
                        SELECT NULL AS "TIME",
                               NULL AS "THING_ID",
                               NULL AS "ID"
                        LIMIT 0
                """

                location_view = """
                    CREATE OR REPLACE VIEW "LOCATIONS" AS
                        SELECT "sl"."id" AS "ID",
                               "sl"."name" AS "NAME",
                               "sl"."description" AS "DESCRIPTION",
                               "sl"."properties" AS "PROPERTIES",
                               "sl"."encoding_type" AS "ENCODING_TYPE",
                               json_build_object(
                                    'type', 'Feature',
                                    'geometry', json_build_object(
                                        'type', 'Point',
                                        'coordinates', json_build_array(
                                            "sl"."latitude",
                                            "sl"."longitude"
                                        ) 
                                    ) 
                               ) AS "LOCATION",
                               NULL AS "GEOM",
                               NULL AS "GEN_FOI_ID"
                        FROM sites_location sl
                """

                observation_view = """"""

                observed_property_view = """
                    CREATE OR REPLACE VIEW "OBS_PROPERTIES" AS
                        SELECT "so"."id" AS "ID",
                               "so"."name" AS "NAME",
                               "so"."description" AS "DESCRIPTION",
                               "so"."definition" AS "DEFINITION",
                               (
                                    SELECT row_to_json(props)
                                    FROM (
                                        VALUES ('test', 'test')
                                    ) AS props ("variableType", "variableCode")
                               ) AS "PROPERTIES"
                        FROM sites_observedproperty so
                """

                sensor_view = """
                    CREATE OR REPLACE VIEW "SENSORS" AS
                        SELECT "ss"."id" AS "ID",
                               "ss"."name" AS "NAME",
                               "ss"."description" AS "DESCRIPTION",
                               "ss"."encoding_type" AS "ENCODING_TYPE",
                               '{}'::json AS "PROPERTIES",
                               (
                                    SELECT row_to_json(props)
                                    FROM (
                                        VALUES ('test', 'test', 'test', '{"sensorManufacturerName": "test", "sensorModelName": "test", "sensorModelURL": "test"}'::json)
                                    ) AS props ("methodCode", "methodType", "methodLink", "sensorModel")
                               ) AS "METADATA"
                        FROM sites_sensor ss
                """

                thing_view = """
                    CREATE OR REPLACE VIEW "THINGS" AS
                        SELECT "st"."id" AS "ID",
                               "st"."name" AS "NAME",
                               "st"."description" AS "DESCRIPTION",
                               (
                                    SELECT row_to_json(props)
                                    FROM (
                                        VALUES ('test', 'test', 'test', 'test', 'test')
                                    ) AS props ("samplingFeatureType", "samplingFeatureCode", "siteType", "state", "county")
                               ) AS "PROPERTIES"
                        FROM sites_thing st
                """

                thing_location_view = """
                    CREATE OR REPLACE VIEW "THINGS_LOCATIONS" AS
                        SELECT "sl"."id" AS "LOCATION_ID",
                               "sl"."thing_id"  AS "THING_ID"
                        FROM sites_location sl
                """

                location_historical_location_view = """
                    CREATE OR REPLACE VIEW "LOCATIONS_HIST_LOCATIONS" AS
                        SELECT NULL AS "LOCATION_ID",
                               NULL  AS "HIST_LOCATION_ID"
                        LIMIT 0
                """

                cursor.execute(feature_of_interest_view)
                cursor.execute(historical_location_view)
                cursor.execute(location_view)

                cursor.execute(observed_property_view)
                cursor.execute(sensor_view)
                cursor.execute(thing_view)
                cursor.execute(thing_location_view)
                cursor.execute(location_historical_location_view)
