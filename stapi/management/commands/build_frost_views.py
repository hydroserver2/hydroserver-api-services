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
                cursor.execute('CREATE EXTENSION IF NOT EXISTS "postgis";')

                datastream_view = """
                    CREATE OR REPLACE VIEW "DATASTREAMS" AS
                        SELECT "sd"."id" AS "ID",
                               "sd"."name" AS "NAME",
                               "sd"."description" AS "DESCRIPTION",
                               "sd"."sensor_id" AS "SENSOR_ID",
                               "sd"."thing_id" AS "THING_ID",
                               "sd"."observed_property_id" AS "OBS_PROPERTY_ID",
                               NULL AS "LAST_FOI_ID",
                               "su"."name" AS "UNIT_NAME",
                               "su"."symbol" AS "UNIT_SYMBOL",
                               "su"."definition" AS "UNIT_DEFINITION",
                               NULL AS "OBSERVED_AREA",
                               "sd"."phenomenon_start_time" AS "PHENOMENON_TIME_START",
                               "sd"."phenomenon_end_time" AS "PHENOMENON_TIME_END",
                               "sd"."result_begin_time" AS "RESULT_TIME_START",
                               "sd"."result_end_time" AS "RESULT_TIME_END",
                               "sd"."observation_type" AS "OBSERVATION_TYPE",
                               json_build_object(
                                    'resultType', "sd"."result_type",
                                    'status', "sd"."status",
                                    'sampledMedium', "sd"."sampled_medium",
                                    'valueCount', "sd"."value_count",
                                    'noDataValue', "sd"."no_data_value",
                                    'processingLevelCode', "sp"."processing_level_code",
                                    'intendedTimeSpacing', "sd"."intended_time_spacing",
                                    'intendedTimeSpacingUnits', "sd"."intended_time_spacing_units",
                                    'aggregationStatistic', "sd"."aggregation_statistic",
                                    'timeAggregationInterval', "sd"."time_aggregation_interval",
                                    'timeAggregationIntervalUnitsName', "sau"."name"
                               ) AS "PROPERTIES"
                        FROM sites_datastream sd
                        LEFT OUTER JOIN sites_unit su ON "sd"."unit_id" = "su"."id"
                        LEFT OUTER JOIN sites_processinglevel sp ON "sd"."processing_level_id" = "sp"."id"
                        LEFT OUTER JOIN sites_unit sau ON "sd"."time_aggregation_interval_units_id" = "sau"."id"
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
                        SELECT "sl"."thing_id" AS "ID",
                               "sl"."name" AS "NAME",
                               "sl"."description" AS "DESCRIPTION",
                               json_build_object(
                                    'city', "sl"."city",
                                    'state', "sl"."state",
                                    'country', "sl"."country",
                                    'elevation_m', "sl"."elevation_m",
                                    'elevationDatum', "sl"."elevation_datum"
                               ) AS "PROPERTIES",
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

                observation_view = """
                    CREATE OR REPLACE VIEW "OBSERVATIONS" AS
                        SELECT "so"."id" AS "ID",
                               "so"."datastream_id" AS "DATASTREAM_ID",
                               "so"."result_time" AS "RESULT_TIME",
                               "so"."result" AS "RESULT_NUMBER",
                               1 AS "RESULT_TYPE",
                               NULL AS "RESULT_BOOLEAN",
                               NULL AS "RESULT_JSON",
                               NULL AS "RESULT_STRING",
                               "so"."result_quality" AS "RESULT_QUALITY",
                               '{}'::json AS "PARAMETERS",
                               NULL AS "FEATURE_ID",
                               NULL AS "MULTI_DATASTREAM_ID",
                               "so"."valid_begin_time" AS "VALID_TIME_START",
                               "so"."valid_end_time" AS "VALID_TIME_END",
                               "so"."phenomenon_time" AS "PHENOMENON_TIME_START",
                               "so"."phenomenon_time" AS "PHENOMENON_TIME_END"
                        FROM sites_observation so
                """

                observed_property_view = """
                    CREATE OR REPLACE VIEW "OBS_PROPERTIES" AS
                        SELECT "so"."id" AS "ID",
                               "so"."name" AS "NAME",
                               "so"."description" AS "DESCRIPTION",
                               "so"."definition" AS "DEFINITION",
                               json_build_object(
                                    'variableCode', "so"."variable_code",
                                    'variableType', "so"."variable_type"
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
                               json_build_object(
                                    'methodCode', "ss"."method_code",
                                    'methodType', "ss"."method_type",
                                    'methodLink', "ss"."method_link",
                                    'sensorModel', json_build_object(
                                        'sensorModelName', "ss"."model",
                                        'sensorManufacturerName', "ss"."manufacturer",
                                        'sensorModelURL', "ss"."model_url"
                                    )
                               ) AS "METADATA"
                        FROM sites_sensor ss
                """

                thing_view = """
                    CREATE OR REPLACE VIEW "THINGS" AS
                        SELECT "st"."id" AS "ID",
                               "st"."name" AS "NAME",
                               "st"."description" AS "DESCRIPTION",
                               json_build_object(
                                    'samplingFeatureType', "st"."sampling_feature_type",
                                    'samplingFeatureCode', "st"."sampling_feature_code",
                                    'siteType', "st"."site_type"
                               ) AS "PROPERTIES"
                        FROM sites_thing st
                """

                thing_location_view = """
                    CREATE OR REPLACE VIEW "THINGS_LOCATIONS" AS
                        SELECT "sl"."thing_id" AS "LOCATION_ID",
                               "sl"."thing_id"  AS "THING_ID"
                        FROM sites_location sl
                """

                location_historical_location_view = """
                    CREATE OR REPLACE VIEW "LOCATIONS_HIST_LOCATIONS" AS
                        SELECT NULL AS "LOCATION_ID",
                               NULL  AS "HIST_LOCATION_ID"
                        LIMIT 0
                """

                cursor.execute(datastream_view)
                cursor.execute(feature_of_interest_view)
                cursor.execute(historical_location_view)
                cursor.execute(location_view)
                cursor.execute(observation_view)
                cursor.execute(observed_property_view)
                cursor.execute(sensor_view)
                cursor.execute(thing_view)
                cursor.execute(thing_location_view)
                cursor.execute(location_historical_location_view)
