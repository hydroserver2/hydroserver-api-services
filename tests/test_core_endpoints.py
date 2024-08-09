import pytest
import json
from collections import Counter
from django.test import Client


@pytest.fixture
def base_url():
    return '/api/data'


@pytest.mark.parametrize(
    'endpoint, method, user, max_queries, expected_response_code, request_body, expected_response', [
        (  # Test GET Things as anonymous user.
                'things', 'get', 'anonymous', 3, 200, None,
                '[{"id": "76dadda5-224b-4e1f-8570-e385bd482b2d", "name": "Taggart Student Center", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "TSC", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.743042, "longitude": -111.81325, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": false, "ownsThing": false, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}], "tags": [{"id": "a12526b9-00c7-4cfd-a49a-d45514e74462", "key": "Code", "value": "20"}]}, {"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": false, "ownsThing": false, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}, {"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}]}]'
        ),
        (  # Test GET Things as active user.
                'things', 'get', 'alice', 4, 200, None,
                '[{"id": "76dadda5-224b-4e1f-8570-e385bd482b2d", "name": "Taggart Student Center", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "TSC", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.743042, "longitude": -111.81325, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}], "tags": [{"id": "a12526b9-00c7-4cfd-a49a-d45514e74462", "key": "Code", "value": "20"}]}, {"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}, {"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}]}, {"id": "e1f18e11-4130-485b-ad67-18f7f44187f8", "name": "USU Technology Building", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "TECH", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.743243, "longitude": -111.808352, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}, {"id": "819260c8-2543-4046-b8c4-7431243ed7c5", "name": "Merrill-Cazier Library", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "LIB", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.742008, "longitude": -111.80972, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}, {"id": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "name": "Maverik Stadium", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "MAVST", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.752026, "longitude": -111.811572, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}], "tags": [{"id": "fb2db25f-0cf2-4bc6-ab15-282d924d2790", "key": "Code", "value": "20"}]}]'
        ),
        (  # Test GET Things with 'modified_since' parameter.
                'things?modified_since=2090-01-01T11:11:11Z', 'get', 'alice', 2, 200, None,
                '[]'
        ),
        (  # Test GET Things with 'owned_only' parameter as active user.
                'things?owned_only=true', 'get', 'bob', 4, 200, None,
                '[{"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": false, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}, {"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}]}, {"id": "819260c8-2543-4046-b8c4-7431243ed7c5", "name": "Merrill-Cazier Library", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "LIB", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.742008, "longitude": -111.80972, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": false, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}, {"id": "e1f18e11-4130-485b-ad67-18f7f44187f8", "name": "USU Technology Building", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "TECH", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.743243, "longitude": -111.808352, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": false, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}]'
        ),
        (  # Test GET Things with 'owned_only' parameter as anonymous user.
                'things?owned_only=true', 'get', 'anonymous', 1, 200, None,
                '[]'
        ),
        (  # Test GET Things with 'primary_owned_only' parameter as active user.
                'things?primary_owned_only=true', 'get', 'alice', 4, 200, None,
                '[{"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}, {"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}]}, {"id": "76dadda5-224b-4e1f-8570-e385bd482b2d", "name": "Taggart Student Center", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "TSC", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.743042, "longitude": -111.81325, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}], "tags": [{"id": "a12526b9-00c7-4cfd-a49a-d45514e74462", "key": "Code", "value": "20"}]}, {"id": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "name": "Maverik Stadium", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "MAVST", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.752026, "longitude": -111.811572, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}], "tags": [{"id": "fb2db25f-0cf2-4bc6-ab15-282d924d2790", "key": "Code", "value": "20"}]}, {"id": "819260c8-2543-4046-b8c4-7431243ed7c5", "name": "Merrill-Cazier Library", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "LIB", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.742008, "longitude": -111.80972, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}, {"id": "e1f18e11-4130-485b-ad67-18f7f44187f8", "name": "USU Technology Building", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "TECH", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.743243, "longitude": -111.808352, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}]'
        ),
        (  # Test GET Things with 'primary_owned_only' parameter as anonymous user.
                'things?primary_owned_only=true', 'get', 'anonymous', 1, 200, None,
                '[]'
        ),
        (  # Test GET Thing metadata as anonymous user.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/metadata', 'get', 'anonymous', 6, 200, None,
                '{"units": [{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}], "sensors": [{"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}], "processingLevels": [{"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}], "observedProperties": [{"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}]}'
        ),
        (  # Test GET Datastreams for a Thing as anonymous user.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/datastreams', 'get', 'anonymous', 2, 200, None,
                '[{"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "c9ef4139-66c6-4eee-ab7e-a4c12111f498", "name": "TSC Temperature - Empty", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams for a Thing as an active user.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/datastreams', 'get', 'alice', 3, 200, None,
                '[{"id": "1b98de60-0386-4d98-a933-b3cd0c09d98e", "name": "TSC Temperature - Private", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "c9ef4139-66c6-4eee-ab7e-a4c12111f498", "name": "TSC Temperature - Empty", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Tags for a Thing as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', 'get', 'anonymous', 3, 200, None,
                '[{"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}, {"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}]'
        ),
        (  # Test GET Tags for a Thing as an active user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', 'get', 'alice', 4, 200, None,
                '[{"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}, {"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}]'
        ),
        (  # Test GET Tags for a Thing as a non-owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', 'get', 'carol', 4, 200, None,
                '[{"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}, {"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}]'
        ),
        (  # Test GET Tags for a Thing as a secondary owner.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags', 'get', 'alice', 4, 200, None,
                '[{"id": "fb2db25f-0cf2-4bc6-ab15-282d924d2790", "key": "Code", "value": "20"}]'
        ),
        (  # Test GET Tags for a private Thing as an anonymous user.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags', 'get', 'anonymous', 1, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Tags for a private Thing as a non-owner.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags', 'get', 'carol', 2, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Tags for a non-existent Thing.
                'things/00000000-0000-0000-0000-000000000000/tags', 'get', 'anonymous', 1, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Photos for a Thing as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', 'get', 'anonymous', 3, 200, None,
                '[{"id": "ada2c09b-27d7-4b57-87d4-a859c6d9368f", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg"}, {"id": "d42158a0-4eda-4542-88a1-21b622e5275e", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/d42158a0-4eda-4542-88a1-21b622e5275e.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/d42158a0-4eda-4542-88a1-21b622e5275e.jpeg"}]'
        ),
        (  # Test GET Photos for a Thing as an active user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', 'get', 'alice', 4, 200, None,
                '[{"id": "ada2c09b-27d7-4b57-87d4-a859c6d9368f", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg"}, {"id": "d42158a0-4eda-4542-88a1-21b622e5275e", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/d42158a0-4eda-4542-88a1-21b622e5275e.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/d42158a0-4eda-4542-88a1-21b622e5275e.jpeg"}]'
        ),
        (  # Test GET Photos for a Thing as a non-owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', 'get', 'carol', 4, 200, None,
                '[{"id": "ada2c09b-27d7-4b57-87d4-a859c6d9368f", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg"}, {"id": "d42158a0-4eda-4542-88a1-21b622e5275e", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/d42158a0-4eda-4542-88a1-21b622e5275e.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/d42158a0-4eda-4542-88a1-21b622e5275e.jpeg"}]'
        ),
        (  # Test GET Photos for a private Thing as a secondary owner.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', 'get', 'alice', 4, 200, None,
                '[{"id": "c74bf8cb-5855-49e6-97c9-546d2e8bc07f", "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "filePath": "/photos/80037b7c-f833-472a-a0d1-7bc40e015ea7/c74bf8cb-5855-49e6-97c9-546d2e8bc07f.jpeg", "link": "http://127.0.0.1:3030/photos/80037b7c-f833-472a-a0d1-7bc40e015ea7/c74bf8cb-5855-49e6-97c9-546d2e8bc07f.jpeg"}]'
        ),
        (  # Test GET Photos for a private Thing as an anonymous user.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', 'get', 'anonymous', 1, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Photos for a private Thing as a non-owner.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', 'get', 'carol', 2, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Photos for a non-existent Thing as an anonymous user.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos', 'get', 'carol', 2, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Observed Properties as an anonymous user.
                'observed-properties', 'get', 'anonymous', 3, 200, None,
                '[{"id": "2f89ca87-667f-4de9-b850-715db3cbf927", "name": "Velocity", "definition": "http://www.example.com/velocity", "description": "A test property.", "type": "Variable", "code": "VELO", "owner": "alice@example.com"}, {"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}, {"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}, {"id": "c1479bbc-3d7e-449c-ad3a-0a1c7742b460", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "bob@example.com"}]'
        ),
        (  # Test GET Observed Properties as an active user.
                'observed-properties', 'get', 'alice', 3, 200, None,
                '[{"id": "2f89ca87-667f-4de9-b850-715db3cbf927", "name": "Velocity", "definition": "http://www.example.com/velocity", "description": "A test property.", "type": "Variable", "code": "VELO", "owner": "alice@example.com"}, {"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}, {"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}, {"id": "c1479bbc-3d7e-449c-ad3a-0a1c7742b460", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "bob@example.com"}]'
        ),
        (  # Test GET Observed Properties owned by authenticated user.
                'observed-properties?owner=currentUser', 'get', 'alice', 3, 200, None,
                '[{"id": "2f89ca87-667f-4de9-b850-715db3cbf927", "name": "Velocity", "definition": "http://www.example.com/velocity", "description": "A test property.", "type": "Variable", "code": "VELO", "owner": "alice@example.com"}, {"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}]'
        ),
        (  # Test GET unowned Observed Properties.
                'observed-properties?owner=noUser', 'get', 'alice', 3, 200, None,
                '[{"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}]'
        ),
        (  # Test GET Observed Properties that are unowned or owned by the authenticated user.
                'observed-properties?owner=currentUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}, {"id": "2f89ca87-667f-4de9-b850-715db3cbf927", "name": "Velocity", "definition": "http://www.example.com/velocity", "description": "A test property.", "type": "Variable", "code": "VELO", "owner": "alice@example.com"}, {"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}]'
        ),
        (  # Test GET Observed Properties that are owned by a user.
                'observed-properties?owner=anyUser', 'get', 'alice', 3, 200, None,
                '[{"id": "2f89ca87-667f-4de9-b850-715db3cbf927", "name": "Velocity", "definition": "http://www.example.com/velocity", "description": "A test property.", "type": "Variable", "code": "VELO", "owner": "alice@example.com"}, {"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}, {"id": "c1479bbc-3d7e-449c-ad3a-0a1c7742b460", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "bob@example.com"}]'
        ),
        (  # Test GET owned and unowned Observed Properties.
                'observed-properties?owner=anyUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "2f89ca87-667f-4de9-b850-715db3cbf927", "name": "Velocity", "definition": "http://www.example.com/velocity", "description": "A test property.", "type": "Variable", "code": "VELO", "owner": "alice@example.com"}, {"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}, {"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}, {"id": "c1479bbc-3d7e-449c-ad3a-0a1c7742b460", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "bob@example.com"}]'
        ),
        (  # Test GET Sensors as an anonymous user.
                'sensors', 'get', 'anonymous', 3, 200, None,
                '[{"id": "5fbab69a-810b-4044-bfac-c40a05634c5c", "name": "test_sensor_2", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "bob@example.com"}, {"id": "a8617070-146a-4e82-8b4d-9a6563de6265", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}]'
        ),
        (  # Test GET Sensors as an active user.
                'sensors', 'get', 'alice', 3, 200, None,
                '[{"id": "5fbab69a-810b-4044-bfac-c40a05634c5c", "name": "test_sensor_2", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "bob@example.com"}, {"id": "a8617070-146a-4e82-8b4d-9a6563de6265", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}]'
        ),
        (  # Test GET Sensors owned by authenticated user.
                'sensors?owner=currentUser', 'get', 'alice', 3, 200, None,
                '[{"id": "a8617070-146a-4e82-8b4d-9a6563de6265", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}]'
        ),
        (  # Test GET unowned Sensors.
                'sensors?owner=noUser', 'get', 'alice', 3, 200, None,
                '[{"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}]'
        ),
        (  # Test GET Sensors that are unowned or owned by the authenticated user.
                'sensors?owner=currentUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "a8617070-146a-4e82-8b4d-9a6563de6265", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}]'
        ),
        (  # Test GET Sensors that are owned by a user.
                'sensors?owner=anyUser', 'get', 'alice', 3, 200, None,
                '[{"id": "5fbab69a-810b-4044-bfac-c40a05634c5c", "name": "test_sensor_2", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "bob@example.com"}, {"id": "a8617070-146a-4e82-8b4d-9a6563de6265", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}]'
        ),
        (  # Test GET owned and unowned Sensors.
                'sensors?owner=anyUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "5fbab69a-810b-4044-bfac-c40a05634c5c", "name": "test_sensor_2", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "bob@example.com"}, {"id": "a8617070-146a-4e82-8b4d-9a6563de6265", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}, {"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}]'
        ),
        (  # Test GET Processing Levels as an anonymous user.
                'processing-levels', 'get', 'anonymous', 3, 200, None,
                '[{"id": "57d48dd3-0fc7-4127-8e34-99c4441c7b68", "code": "1", "definition": "Processed", "explanation": "Data is processed.", "owner": "alice@example.com"}, {"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}, {"id": "fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "bob@example.com"}, {"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET Processing Levels as an active user.
                'processing-levels', 'get', 'alice', 3, 200, None,
                '[{"id": "57d48dd3-0fc7-4127-8e34-99c4441c7b68", "code": "1", "definition": "Processed", "explanation": "Data is processed.", "owner": "alice@example.com"}, {"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}, {"id": "fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "bob@example.com"}, {"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET Processing Levels owned by authenticated user.
                'processing-levels?owner=currentUser', 'get', 'alice', 3, 200, None,
                '[{"id": "57d48dd3-0fc7-4127-8e34-99c4441c7b68", "code": "1", "definition": "Processed", "explanation": "Data is processed.", "owner": "alice@example.com"}, {"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET unowned Processing Levels.
                'processing-levels?owner=noUser', 'get', 'alice', 3, 200, None,
                '[{"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}]'
        ),
        (  # Test GET Processing Levels that are unowned or owned by the authenticated user.
                'processing-levels?owner=currentUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "57d48dd3-0fc7-4127-8e34-99c4441c7b68", "code": "1", "definition": "Processed", "explanation": "Data is processed.", "owner": "alice@example.com"}, {"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}, {"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET Processing Levels that are owned by a user.
                'processing-levels?owner=anyUser', 'get', 'alice', 3, 200, None,
                '[{"id": "57d48dd3-0fc7-4127-8e34-99c4441c7b68", "code": "1", "definition": "Processed", "explanation": "Data is processed.", "owner": "alice@example.com"}, {"id": "fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "bob@example.com"}, {"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET owned and unowned Processing Levels.
                'processing-levels?owner=anyUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "57d48dd3-0fc7-4127-8e34-99c4441c7b68", "code": "1", "definition": "Processed", "explanation": "Data is processed.", "owner": "alice@example.com"}, {"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}, {"id": "fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "bob@example.com"}, {"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET Result Qualifiers as an anonymous user.
                'result-qualifiers', 'get', 'anonymous', 3, 200, None,
                '[{"id": "3064f342-f614-41a7-8748-246a711e5175", "code": "E", "description": "Estimated value.", "owner": "alice@example.com"}, {"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}, {"id": "7f2efa17-96f4-4fda-a9dc-fdcd9e553faa", "code": "PF", "description": "Power failure.", "owner": "alice@example.com"}, {"id": "16508aef-ade0-43fb-9402-bee06974960b", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "bob@example.com"}, {"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}]'
        ),
        (  # Test GET Result Qualifiers as an active user.
                'result-qualifiers', 'get', 'alice', 3, 200, None,
                '[{"id": "3064f342-f614-41a7-8748-246a711e5175", "code": "E", "description": "Estimated value.", "owner": "alice@example.com"}, {"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}, {"id": "7f2efa17-96f4-4fda-a9dc-fdcd9e553faa", "code": "PF", "description": "Power failure.", "owner": "alice@example.com"}, {"id": "16508aef-ade0-43fb-9402-bee06974960b", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "bob@example.com"}, {"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}]'
        ),
        (  # Test GET Result Qualifiers owned by authenticated user.
                'result-qualifiers?owner=currentUser', 'get', 'alice', 3, 200, None,
                '[{"id": "3064f342-f614-41a7-8748-246a711e5175", "code": "E", "description": "Estimated value.", "owner": "alice@example.com"}, {"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}, {"id": "7f2efa17-96f4-4fda-a9dc-fdcd9e553faa", "code": "PF", "description": "Power failure.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET unowned Result Qualifiers.
                'result-qualifiers?owner=noUser', 'get', 'alice', 3, 200, None,
                '[{"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}]'
        ),
        (  # Test GET Result Qualifiers that are unowned or owned by the authenticated user.
                'result-qualifiers?owner=currentUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "3064f342-f614-41a7-8748-246a711e5175", "code": "E", "description": "Estimated value.", "owner": "alice@example.com"}, {"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}, {"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}, {"id": "7f2efa17-96f4-4fda-a9dc-fdcd9e553faa", "code": "PF", "description": "Power failure.", "owner": "alice@example.com"}]'
        ),
        (  # Test GET Result Qualifiers that are owned by a user.
                'result-qualifiers?owner=anyUser', 'get', 'alice', 3, 200, None,
                '[{"id": "3064f342-f614-41a7-8748-246a711e5175", "code": "E", "description": "Estimated value.", "owner": "alice@example.com"}, {"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}, {"id": "7f2efa17-96f4-4fda-a9dc-fdcd9e553faa", "code": "PF", "description": "Power failure.", "owner": "alice@example.com"}, {"id": "16508aef-ade0-43fb-9402-bee06974960b", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "bob@example.com"}]'
        ),
        (  # Test GET owned and unowned Result Qualifiers.
                'result-qualifiers?owner=anyUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "3064f342-f614-41a7-8748-246a711e5175", "code": "E", "description": "Estimated value.", "owner": "alice@example.com"}, {"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}, {"id": "7f2efa17-96f4-4fda-a9dc-fdcd9e553faa", "code": "PF", "description": "Power failure.", "owner": "alice@example.com"}, {"id": "16508aef-ade0-43fb-9402-bee06974960b", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "bob@example.com"}, {"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}]'
        ),
        (  # Test GET Units as an anonymous user.
                'units', 'get', 'anonymous', 3, 200, None,
                '[{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}, {"id": "23bd903d-36f2-4572-b2e2-fd0a55c00498", "name": "Feet per second", "symbol": "FPS", "definition": "http://www.example.com/feet-per-second", "type": "Unit", "owner": "alice@example.com"}, {"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}, {"id": "054ac53a-520f-4340-96f1-889ffa12874b", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "bob@example.com"}]'
        ),
        (  # Test GET Units as an active user.
                'units', 'get', 'alice', 3, 200, None,
                '[{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}, {"id": "23bd903d-36f2-4572-b2e2-fd0a55c00498", "name": "Feet per second", "symbol": "FPS", "definition": "http://www.example.com/feet-per-second", "type": "Unit", "owner": "alice@example.com"}, {"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}, {"id": "054ac53a-520f-4340-96f1-889ffa12874b", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "bob@example.com"}]'
        ),
        (  # Test GET Units owned by authenticated user.
                'units?owner=currentUser', 'get', 'alice', 3, 200, None,
                '[{"id": "23bd903d-36f2-4572-b2e2-fd0a55c00498", "name": "Feet per second", "symbol": "FPS", "definition": "http://www.example.com/feet-per-second", "type": "Unit", "owner": "alice@example.com"}, {"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}]'
        ),
        (  # Test GET unowned Units.
                'units?owner=noUser', 'get', 'alice', 3, 200, None,
                '[{"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}]'
        ),
        (  # Test GET Units that are unowned or owned by the authenticated user.
                'units?owner=currentUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "23bd903d-36f2-4572-b2e2-fd0a55c00498", "name": "Feet per second", "symbol": "FPS", "definition": "http://www.example.com/feet-per-second", "type": "Unit", "owner": "alice@example.com"}, {"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}, {"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}]'
        ),
        (  # Test GET Units that are owned by a user.
                'units?owner=anyUser', 'get', 'alice', 3, 200, None,
                '[{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}, {"id": "054ac53a-520f-4340-96f1-889ffa12874b", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "bob@example.com"}, {"id": "23bd903d-36f2-4572-b2e2-fd0a55c00498", "name": "Feet per second", "symbol": "FPS", "definition": "http://www.example.com/feet-per-second", "type": "Unit", "owner": "alice@example.com"}]'
        ),
        (  # Test GET owned and unowned Units.
                'units?owner=anyUserOrNoUser', 'get', 'alice', 3, 200, None,
                '[{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}, {"id": "054ac53a-520f-4340-96f1-889ffa12874b", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "bob@example.com"}, {"id": "23bd903d-36f2-4572-b2e2-fd0a55c00498", "name": "Feet per second", "symbol": "FPS", "definition": "http://www.example.com/feet-per-second", "type": "Unit", "owner": "alice@example.com"}, {"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}]'
        ),
        (  # Test GET Data Loaders as an anonymous user.
                'data-loaders', 'get', 'anonymous', 3, 200, None,
                '[]'
        ),
        (  # Test GET Data Loaders as an active user.
                'data-loaders', 'get', 'alice', 3, 200, None,
                '[{"id": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "name": "Alice\'s Streaming Data Loader"}, {"id": "eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd", "name": "Alice\'s Old Streaming Data Loader"}]'
        ),
        (  # Test GET Data Sources for a Data Loader as an anonymous user.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', 'get', 'anonymous', 3, 404, None,
                '{"detail": "Data loader not found."}'
        ),
        (  # Test GET Data Sources for a Data Loader as an owner.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', 'get', 'alice', 3, 200, None,
                '[{"id": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "name": "Test Data Source", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}, {"id": "91783bce-b13a-42f7-ab22-4282c6303c42", "name": "Test Data Source - Delete", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}]'
        ),
        (  # Test GET Data Sources for a Data Loader as a non-owner.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e/data-sources', 'get', 'bob', 3, 404, None,
                '{"detail": "Data loader not found."}'
        ),
        (  # Test GET Data Sources as an anonymous user.
                'data-sources', 'get', 'anonymous', 3, 200, None,
                '[]'
        ),
        (  # Test GET Data Sources as an active user.
                'data-sources', 'get', 'alice', 3, 200, None,
                '[{"id": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "name": "Test Data Source", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}, {"id": "91783bce-b13a-42f7-ab22-4282c6303c42", "name": "Test Data Source - Delete", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}]'
        ),
        (  # Test GET Datastreams of a Data Source as an anonymous user.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717/datastreams', 'get', 'anonymous', 3, 404, None,
                '{"detail": "Data source not found."}'
        ),
        (  # Test GET Datastreams of a Data Source as an active user.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717/datastreams', 'get', 'alice', 3, 200, None,
                '[{"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams as an anonymous user.
                'datastreams', 'get', 'anonymous', 3, 200, None,
                '[{"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "c9ef4139-66c6-4eee-ab7e-a4c12111f498", "name": "TSC Temperature - Empty", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams as an active user.
                'datastreams', 'get', 'alice', 3, 200, None,
                '[{"id": "1b98de60-0386-4d98-a933-b3cd0c09d98e", "name": "TSC Temperature - Private", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "61895e0e-5395-489e-845b-562d5b93db22", "name": "MAVST Temperature", "description": "Temperature measured at the MAVST.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "c9ef4139-66c6-4eee-ab7e-a4c12111f498", "name": "TSC Temperature - Empty", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "fd22da23-2291-4c14-bcbc-9fdb4671b2cb", "name": "MAVST Temperature - Private", "description": "Temperature measured at the MAVST.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams as secondary owner.
                'datastreams', 'get', 'bob', 3, 200, None,
                '[{"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "c9ef4139-66c6-4eee-ab7e-a4c12111f498", "name": "TSC Temperature - Empty", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams with modified_since parameter.
                'datastreams?modified_since=2090-01-01T11:11:11Z', 'get', 'anonymous', 3, 200, None,
                '[]'
        ),
        (  # Test GET Datastreams owned by user.
                'datastreams?owned_only=true', 'get', 'bob', 3, 200, None,
                '[{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams owned by anonymous user.
                'datastreams?owned_only=true', 'get', 'anonymous', 3, 200, None,
                '[]'
        ),
        (  # Test GET Datastreams primary owned by user.
                'datastreams?primary_owned_only=true', 'get', 'alice', 3, 200, None,
                '[{"id": "1b98de60-0386-4d98-a933-b3cd0c09d98e", "name": "TSC Temperature - Private", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "22074b3e-455a-4a4b-91c3-38e6cf85557d", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "61895e0e-5395-489e-845b-562d5b93db22", "name": "MAVST Temperature", "description": "Temperature measured at the MAVST.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "c9ef4139-66c6-4eee-ab7e-a4c12111f498", "name": "TSC Temperature - Empty", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": null, "phenomenonBeginTime": null, "phenomenonEndTime": null, "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}, {"id": "fd22da23-2291-4c14-bcbc-9fdb4671b2cb", "name": "MAVST Temperature - Private", "description": "Temperature measured at the MAVST.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}]'
        ),
        (  # Test GET Datastreams primary owned by anonymous user.
                'datastreams?primary_owned_only=true', 'get', 'anonymous', 3, 200, None,
                '[]'
        ),
        (  # Test GET Thing as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1', 'get', 'anonymous', 4, 200, None,
                '{"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": false, "ownsThing": false, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}, {"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}]}'
        ),
        (  # Test GET private Thing as an anonymous user.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET non-existent Thing as an anonymous user.
                'things/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET inactive Thing as an anonymous user.
                'things/92a3a099-f2d3-40ec-9b0e-d25ae8bf59b7', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET private Thing as a primary owner.
                'things/819260c8-2543-4046-b8c4-7431243ed7c5', 'get', 'alice', 4, 200, None,
                '{"id": "819260c8-2543-4046-b8c4-7431243ed7c5", "name": "Merrill-Cazier Library", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "LIB", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.742008, "longitude": -111.80972, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}'
        ),
        (   # Test GET private Thing as a secondary owner.
                'things/819260c8-2543-4046-b8c4-7431243ed7c5', 'get', 'bob', 4, 200, None,
                '{"id": "819260c8-2543-4046-b8c4-7431243ed7c5", "name": "Merrill-Cazier Library", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "LIB", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.742008, "longitude": -111.80972, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": true, "isPrimaryOwner": false, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": []}'
        ),
        (  # Test GET private Thing as a non-owner.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7', 'get', 'bob', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Tag as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 'get', 'anonymous', 4, 200, None,
                '{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}'
        ),
        (  # Test GET Tag as a primary owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 'get', 'alice', 4, 200, None,
                '{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}'
        ),
        (  # Test GET Tag as a secondary owner
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags/fb2db25f-0cf2-4bc6-ab15-282d924d2790', 'get', 'alice', 4, 200, None,
                '{"id": "fb2db25f-0cf2-4bc6-ab15-282d924d2790", "key": "Code", "value": "20"}'
        ),
        (  # Test GET private Tag as an anonymous user.
                'things/00000000-0000-0000-0000-000000000000/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET non-existent Tag as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Tag with the given ID was not found."}'
        ),
        (  # Test GET Tag of private Thing as an anonymous user.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/tags/fb2db25f-0cf2-4bc6-ab15-282d924d2790', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Photo as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos/ada2c09b-27d7-4b57-87d4-a859c6d9368f', 'get', 'anonymous', 4, 200, None,
                '{"id": "ada2c09b-27d7-4b57-87d4-a859c6d9368f", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg"}'
        ),
        (  # Test GET Photo as a primary owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos/ada2c09b-27d7-4b57-87d4-a859c6d9368f', 'get', 'alice', 4, 200, None,
                '{"id": "ada2c09b-27d7-4b57-87d4-a859c6d9368f", "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "filePath": "/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg", "link": "http://127.0.0.1:3030/photos/3b7818af-eff7-4149-8517-e5cad9dc22e1/ada2c09b-27d7-4b57-87d4-a859c6d9368f.jpeg"}'
        ),
        (  # Test GET Photo as a secondary owner.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos/c74bf8cb-5855-49e6-97c9-546d2e8bc07f', 'get', 'alice', 4, 200, None,
                '{"id": "c74bf8cb-5855-49e6-97c9-546d2e8bc07f", "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "filePath": "/photos/80037b7c-f833-472a-a0d1-7bc40e015ea7/c74bf8cb-5855-49e6-97c9-546d2e8bc07f.jpeg", "link": "http://127.0.0.1:3030/photos/80037b7c-f833-472a-a0d1-7bc40e015ea7/c74bf8cb-5855-49e6-97c9-546d2e8bc07f.jpeg"}'
        ),
        (  # Test GET Photo of non-existent Thing as an anonymous user.
                'things/00000000-0000-0000-0000-000000000000/photos/ada2c09b-27d7-4b57-87d4-a859c6d9368f', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET non-existent Photo as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Photo with the given ID was not found."}'
        ),
        (  # Test GET Photo of private Thing as an anonymous user.
                'things/80037b7c-f833-472a-a0d1-7bc40e015ea7/photos/c74bf8cb-5855-49e6-97c9-546d2e8bc07f', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Thing not found."}'
        ),
        (  # Test GET Observed Property as an anonymous user.
                'observed-properties/11e37e36-3d65-497a-b432-e238ec45195b', 'get', 'anonymous', 2, 200, None,
                '{"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}'
        ),
        (  # Test GET Observed Property as an active user.
                'observed-properties/11e37e36-3d65-497a-b432-e238ec45195b', 'get', 'alice', 2, 200, None,
                '{"id": "11e37e36-3d65-497a-b432-e238ec45195b", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": null}'
        ),
        (  # Test GET owned Observed Property as an anonymous user.
                'observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 'get', 'anonymous', 2, 200, None,
                '{"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Observed Property as an active user.
                'observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 'get', 'alice', 2, 200, None,
                '{"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Observed Property as a non-owner.
                'observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 'get', 'bob', 2, 200, None,
                '{"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}'
        ),
        (  # Test GET non-existent Observed Property as an anonymous user.
                'observed-properties/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Observed property not found."}'
        ),
        (  # Test GET inactive Observed Property as an anonymous user.
                'observed-properties/b6bfee6e-b8d6-46cd-972a-bdd56bd41bd1', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Observed property not found."}'
        ),
        (  # Test GET Processing Level as an anonymous user.
                'processing-levels/caab642c-14f9-4823-8517-9b1bce59f626', 'get', 'anonymous', 2, 200, None,
                '{"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}'
        ),
        (  # Test GET Processing Level as an active user.
                'processing-levels/caab642c-14f9-4823-8517-9b1bce59f626', 'get', 'alice', 2, 200, None,
                '{"id": "caab642c-14f9-4823-8517-9b1bce59f626", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": null}'
        ),
        (  # Test GET owned Processing Level as an anonymous user.
                'processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'get', 'anonymous', 2, 200, None,
                '{"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Processing Level as an active user.
                'processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'get', 'alice', 2, 200, None,
                '{"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Processing Level as a non-owner.
                'processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'get', 'bob', 2, 200, None,
                '{"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}'
        ),
        (  # Test GET non-existent Processing Level as an anonymous user.
                'processing-levels/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Processing level not found."}'
        ),
        (  # Test GET inactive Processing Level as an anonymous user.
                'processing-levels/2a92ca50-fe96-438b-bc1c-7efb09427383', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Processing level not found."}'
        ),
        (  # Test GET Result Qualifier as an anonymous user.
                'result-qualifiers/7a6a3957-f45f-4a00-9edf-d1e53a689538', 'get', 'anonymous', 2, 200, None,
                '{"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}'
        ),
        (  # Test GET Result Qualifier as an active user.
                'result-qualifiers/7a6a3957-f45f-4a00-9edf-d1e53a689538', 'get', 'alice', 2, 200, None,
                '{"id": "7a6a3957-f45f-4a00-9edf-d1e53a689538", "code": "ICE", "description": "Ice formed on the sensor.", "owner": null}'
        ),
        (  # Test GET owned Result Qualifier as an anonymous user.
                'result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 'get', 'anonymous', 2, 200, None,
                '{"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Result Qualifier as an active user.
                'result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 'get', 'alice', 2, 200, None,
                '{"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Result Qualifier as a non-owner.
                'result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 'get', 'bob', 2, 200, None,
                '{"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}'
        ),
        (  # Test GET non-existent Result Qualifier as an anonymous user.
                'result-qualifiers/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Result qualifier not found."}'
        ),
        (  # Test GET inactive Result Qualifier as an anonymous user.
                'result-qualifiers/72ce9a6d-3a8d-4a92-abb8-07924479193f', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Result qualifier not found."}'
        ),
        (  # Test GET Sensor as an anonymous user.
                'sensors/c45c6050-dc52-4a37-a562-66816a6ef1b5', 'get', 'anonymous', 2, 200, None,
                '{"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}'
        ),
        (  # Test GET Sensor as an active user.
                'sensors/c45c6050-dc52-4a37-a562-66816a6ef1b5', 'get', 'alice', 2, 200, None,
                '{"id": "c45c6050-dc52-4a37-a562-66816a6ef1b5", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": null}'
        ),
        (  # Test GET owned Sensor as an anonymous user.
                'sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 'get', 'anonymous', 2, 200, None,
                '{"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Sensor as an active user.
                'sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 'get', 'alice', 2, 200, None,
                '{"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Sensor as a non-owner.
                'sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 'get', 'bob', 2, 200, None,
                '{"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}'
        ),
        (  # Test GET non-existent Sensor as an anonymous user.
                'sensors/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Sensor not found."}'
        ),
        (  # Test GET inactive Sensor as an anonymous user.
                'sensors/41ebe791-3868-4c09-9744-f6954d295edc', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Sensor not found."}'
        ),
        (  # Test GET Unit as an anonymous user.
                'units/a1695fce-bbee-42eb-90da-44c951be7fbd', 'get', 'anonymous', 2, 200, None,
                '{"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}'
        ),
        (  # Test GET Unit as an active user.
                'units/a1695fce-bbee-42eb-90da-44c951be7fbd', 'get', 'alice', 2, 200, None,
                '{"id": "a1695fce-bbee-42eb-90da-44c951be7fbd", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": null}'
        ),
        (  # Test GET owned Unit as an anonymous user.
                'units/967944cb-903b-4f96-afba-3b9e69722f8f', 'get', 'anonymous', 2, 200, None,
                '{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Unit as an active user.
                'units/967944cb-903b-4f96-afba-3b9e69722f8f', 'get', 'alice', 2, 200, None,
                '{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}'
        ),
        (  # Test GET owned Unit as a non-owner.
                'units/967944cb-903b-4f96-afba-3b9e69722f8f', 'get', 'bob', 2, 200, None,
                '{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}'
        ),
        (  # Test GET non-existent Unit as an anonymous user.
                'units/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Unit not found."}'
        ),
        (  # Test GET inactive Unit as an anonymous user.
                'units/20b29933-078d-48b9-95d2-d829ddecd5d8', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Unit not found."}'
        ),
        (  # Test GET Data Loader as an owner.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 'get', 'alice', 2, 200, None,
                '{"id": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "name": "Alice\'s Streaming Data Loader"}'
        ),
        (  # Test GET Data Loader as a non-owner.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 'get', 'bob', 2, 404, None,
                '{"detail": "Data loader not found."}'
        ),
        (  # Test GET Data Loader as an anonymous user.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Data loader not found."}'
        ),
        (  # Test GET Data Source as an owner.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'get', 'alice', 2, 200, None,
                '{"id": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "name": "Test Data Source", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}'
        ),
        (  # Test GET Data Source as a non-owner.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'get', 'bob', 2, 404, None,
                '{"detail": "Data source not found."}'
        ),
        (  # Test GET Data Source as an anonymous user.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'get', 'anonymous', 2, 404, None,
                '{"detail": "Data source not found."}'
        ),
        (  # Test GET Datastream as an anonymous user.
                'datastreams/bf5542df-5500-45b4-aabc-4835534880ff', 'get', 'anonymous', 4, 200, None,
                '{"id": "bf5542df-5500-45b4-aabc-4835534880ff", "name": "TSC Temperature", "description": "Temperature measured at the TSC.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 3, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-03T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "dataSourceColumn": null, "isVisible": true, "isDataVisible": true, "thingId": "76dadda5-224b-4e1f-8570-e385bd482b2d", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test GET private Datastream as an anonymous user.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Datastream not found."}'
        ),
        (  # Test GET non-existent Datastream as an anonymous user.
                'datastreams/00000000-0000-0000-0000-000000000000', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Datastream not found."}'
        ),
        (  # Test GET hidden Datastream as an anonymous user.
                'datastreams/61895e0e-5395-489e-845b-562d5b93db22', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Datastream not found."}'
        ),
        (  # Test GET inactive Datastream as an anonymous user.
                'datastreams/3a028176-ee60-47cc-a573-222dbfbe6b34', 'get', 'anonymous', 4, 404, None,
                '{"detail": "Datastream not found."}'
        ),
        (  # Test GET Datastream as a primary owner.
                'datastreams/fd22da23-2291-4c14-bcbc-9fdb4671b2cb', 'get', 'alice', 4, 200, None,
                '{"id": "fd22da23-2291-4c14-bcbc-9fdb4671b2cb", "name": "MAVST Temperature - Private", "description": "Temperature measured at the MAVST.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "80037b7c-f833-472a-a0d1-7bc40e015ea7", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test GET Datastream as a secondary owner.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'get', 'bob', 4, 200, None,
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test GET private Datastream as a non-owner.
                'datastreams/1b98de60-0386-4d98-a933-b3cd0c09d98e', 'get', 'bob', 4, 404, None,
                '{"detail": "Datastream not found."}'
        ),
        (  # Test POST Thing as an active user.
                'things', 'post', 'alice', 15, 201, {
                    'latitude': 0, 'longitude': 0, 'elevation_m': 0, 'elevationDatum': 'string', 'state': 'string',
                    'county': 'string', 'name': 'string', 'description': 'string', 'samplingFeatureType': 'string',
                    'samplingFeatureCode': 'string', 'siteType': 'string', 'dataDisclaimer': 'string'
                }, None
        ),
        (  # Test POST Thing with bad body.
                'things', 'post', 'alice', 2, 422, {'latitude': 91, 'longitude': -181, 'elevation_m': 100000},
                '{"detail": [{"type": "less_than_equal", "loc": ["body", "data", "latitude"], "msg": "Input should be less than or equal to 90", "ctx": {"le": 90.0}}, {"type": "greater_than_equal", "loc": ["body", "data", "longitude"], "msg": "Input should be greater than or equal to -180", "ctx": {"ge": -180.0}}, {"type": "less_than_equal", "loc": ["body", "data", "elevation_m"], "msg": "Input should be less than or equal to 99999", "ctx": {"le": 99999.0}}, {"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "description"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "samplingFeatureType"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "samplingFeatureCode"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "siteType"], "msg": "Field required"}]}'
        ),
        (  # Test POST Thing as an anonymous user.
                'things', 'post', 'anonymous', 2, 401,  {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Tag as an active user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', 'post', 'alice', 5, 201,  {
                    'key': 'string', 'value': 'string'
                }, None
        ),
        (  # Test POST Tag with bad body.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "key"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "value"], "msg": "Field required"}]}'
        ),
        (  # Test POST Tag as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Photo with a bad body.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["file", "files"], "msg": "Field required"}]}'
        ),
        (  # Test POST Photo as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/photos', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Observed Property as an active user.
                'observed-properties', 'post', 'alice', 5, 201, {
                    'name': 'string', 'description': 'string', 'definition': 'string', 'type': 'string', 'code': 'string'
                }, None
        ),
        (  # Test POST Observed Property with bad body.
                'observed-properties', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "definition"], "msg": "Field required"}]}'
        ),
        (  # Test POST Observed Property as an anonymous user.
                'observed-properties', 'post', 'anonymous', 2, 401,  {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Processing Level as an active user.
                'processing-levels', 'post', 'alice', 5, 201, {
                    'code': 'string', 'definition': 'string', 'explanation': 'string'
                }, None
        ),
        (  # Test POST Processing Level with bad body.
                'processing-levels', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "code"], "msg": "Field required"}]}'
        ),
        (  # Test POST Processing Level as an anonymous user.
                'processing-levels', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Sensor as an active user.
                'sensors', 'post', 'alice', 5, 201, {
                    'name': 'string', 'description': 'string', 'encodingType': 'string', 'methodType': 'string'
                }, None
        ),
        (  # Test POST Sensor with bad body.
                'sensors', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "description"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "encodingType"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "methodType"], "msg": "Field required"}]}'
        ),
        (  # Test POST Sensor as an anonymous user.
                'sensors', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Unit as an active user.
                'units', 'post', 'alice', 5, 201, {
                    'name': 'string', 'symbol': 'string', 'definition': 'string', 'type': 'string'
                }, None
        ),
        (  # Test POST Unit with bad body.
                'units', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "symbol"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "definition"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "type"], "msg": "Field required"}]}'
        ),
        (  # Test POST Unit as an anonymous user.
                'units', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Data Loader as an active user.
                'data-loaders', 'post', 'alice', 5, 201, {
                    'name': 'string'
                }, None
        ),
        (  # Test POST Data Loader with bad body.
                'data-loaders', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}]}'
        ),
        (  # Test POST Data Loader as an anonymous user.
                'data-loaders', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Data Source as an active user.
                'data-sources', 'post', 'alice', 6, 201, {
                    'name': 'string', 'timestampColumn': 'string', 'dataLoaderId': '9d571b4b-c986-4fa8-8933-0491ddad9e0e',
                    'paused': False
                }, None
        ),
        (  # Test POST Data Source linked to unowned Data Loader.
                'data-sources', 'post', 'alice', 6, 403, {
                    'name': 'string', 'timestampColumn': 'string', 'dataLoaderId': '9bcd1dbf-eb1e-47dd-8874-f0a65f16c709',
                    'paused': False
                }, '"You do not have permission to link a data source to the given data loader."'
        ),
        (  # Test POST Data Source with bad body.
                'data-sources', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "paused"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "timestampColumn"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "dataLoaderId"], "msg": "Field required"}]}'
        ),
        (  # Test POST Data Source as an anonymous user.
                'data-sources', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test POST Datastream as an active user.
                'datastreams', 'post', 'alice', 15, 201, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
                    'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
                    'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
                    'timeAggregationIntervalUnits': 'minutes'
                }, None
        ),
        (  # Test POST Datastream as a secondary owner.
                'datastreams', 'post', 'bob', 15, 201, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
                    'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
                    'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
                    'timeAggregationIntervalUnits': 'minutes'
                }, None
        ),
        (  # Test POST Datastream with unowned Thing.
                'datastreams', 'post', 'bob', 15, 404, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '76dadda5-224b-4e1f-8570-e385bd482b2d', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
                    'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
                    'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
                    'timeAggregationIntervalUnits': 'minutes'
                }, '{"detail": "Thing not found."}'
        ),
        (  # Test POST Datastream with unowned Sensor.
                'datastreams', 'post', 'bob', 15, 403, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': '5fbab69a-810b-4044-bfac-c40a05634c5c',
                    'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
                    'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
                    'timeAggregationIntervalUnits': 'minutes'
                }, '"You do not have permission to link a datastream to the given sensor."'
        ),
        (  # Test POST Datastream with unowned Observed Property.
                'datastreams', 'post', 'bob', 15, 403, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
                    'observedPropertyId': 'c1479bbc-3d7e-449c-ad3a-0a1c7742b460',
                    'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
                    'timeAggregationIntervalUnits': 'minutes'
                }, '"You do not have permission to link a datastream to the given observed property."'
        ),
        (  # Test POST Datastream with unowned Processing Level.
                'datastreams', 'post', 'bob', 15, 403, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
                    'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
                    'processingLevelId': 'fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd', 'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f',
                    'timeAggregationIntervalUnits': 'minutes'
                }, '"You do not have permission to link a datastream to the given processing level."'
        ),
        (  # Test POST Datastream with unowned Unit.
                'datastreams', 'post', 'bob', 15, 403, {
                    'name': 'string', 'description': 'string', 'observationType': 'string', 'sampledMedium': 'string',
                    'noDataValue': 0, 'aggregationStatistic': 'string', 'timeAggregationInterval': 0, 'resultType': 'string',
                    'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1', 'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c',
                    'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb',
                    'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'unitId': '054ac53a-520f-4340-96f1-889ffa12874b',
                    'timeAggregationIntervalUnits': 'minutes'
                }, '"You do not have permission to link a datastream to the given unit."'
        ),
        (  # Test POST Datastream with bad body.
                'datastreams', 'post', 'alice', 2, 422, {'test': 'test'},
                '{"detail": [{"type": "missing", "loc": ["body", "data", "name"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "description"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "observationType"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "sampledMedium"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "noDataValue"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "aggregationStatistic"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "timeAggregationInterval"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "resultType"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "thingId"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "sensorId"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "observedPropertyId"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "processingLevelId"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "unitId"], "msg": "Field required"}, {"type": "missing", "loc": ["body", "data", "timeAggregationIntervalUnits"], "msg": "Field required"}]}'
        ),
        (  # Test POST Datastream as an anonymous user.
                'datastreams', 'post', 'anonymous', 2, 401, {'test': 'test'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Thing as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1', 'patch', 'anonymous', 10, 401, {'description': 'A test thing.'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Thing as an owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1', 'patch', 'alice', 10, 203, {'description': 'A test thing.'},
                '{"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": true, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}, {"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}]}'
        ),
        (  # Test PATCH Thing as a secondary owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1', 'patch', 'bob', 10, 203, {'description': 'A test thing.'},
                '{"id": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "name": "Utah Water Research Lab", "description": "A test thing.", "samplingFeatureType": "Site", "samplingFeatureCode": "UWRL", "siteType": "Other", "dataDisclaimer": null, "latitude": 41.739742, "longitude": -111.793766, "elevation_m": 1.0, "elevationDatum": null, "state": "UT", "county": "Cache", "country": null, "isPrivate": false, "isPrimaryOwner": false, "ownsThing": true, "owners": [{"firstName": "Alice", "lastName": "Johnson", "email": "alice@example.com", "organizationName": "Utah State University", "isPrimaryOwner": true}, {"firstName": "Bob", "lastName": "Smith", "email": "bob@example.com", "organizationName": null, "isPrimaryOwner": false}], "tags": [{"id": "9311d773-b1ae-4a5d-b99d-372b16bb138c", "key": "Active", "value": "True"}, {"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}]}'
        ),
        (  # Test PATCH Thing as a non-owner.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d', 'patch', 'bob', 10, 404, {'description': 'A test thing.'},
                '{"detail": "Thing not found."}'
        ),
        (  # Test PATCH Tag as an anonymous user.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 'patch', 'anonymous', 10, 401, {'key': 'Code'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Tag as an owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 'patch', 'alice', 10, 203, {'key': 'Code'},
                '{"id": "8cfabf6b-35d6-48a0-a013-087be9aa0009", "key": "Code", "value": "10"}'
        ),
        (  # Test PATCH Tag as a non-owner.
                'things/3b7818af-eff7-4149-8517-e5cad9dc22e1/tags/8cfabf6b-35d6-48a0-a013-087be9aa0009', 'patch', 'carol', 10, 404, {'key': 'Code'},
                '{"detail": "Thing not found."}'
        ),
        (  # Test PATCH Observed Property as a non-owner.
                'observed-properties/11e37e36-3d65-497a-b432-e238ec45195b', 'patch', 'alice', 6, 404, {'name': 'Temperature'},
                '{"detail": "Observed property not found."}'
        ),
        (  # Test PATCH Observed Property as an anonymous user.
                'observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 'patch', 'anonymous', 6, 401, {'name': 'Temperature'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Observed Property as an owner.
                'observed-properties/cda18a59-3f2c-4c09-976f-3eadc34423bb', 'patch', 'alice', 6, 203, {'name': 'Temperature'},
                '{"id": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "name": "Temperature", "definition": "http://www.example.com/temperature", "description": "A test property.", "type": "Variable", "code": "TEMP", "owner": "alice@example.com"}'
        ),
        (  # Test PATCH Processing Level as a non-owner.
                'processing-levels/caab642c-14f9-4823-8517-9b1bce59f626', 'patch', 'alice', 6, 404, {'definition': 'Raw'},
                '{"detail": "Processing level not found."}'
        ),
        (  # Test PATCH Processing Level as an anonymous user.
                'processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'patch', 'anonymous', 6, 401, {'definition': 'Raw'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Processing Level as an owner.
                'processing-levels/f2e18666-2a5c-4f75-b83b-aebfffc6a39f', 'patch', 'alice', 6, 203, {'definition': 'Raw'},
                '{"id": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "code": "0", "definition": "Raw", "explanation": "Data is unprocessed.", "owner": "alice@example.com"}'
        ),
        (  # Test PATCH Result Qualifier as a non-owner.
                'result-qualifiers/7a6a3957-f45f-4a00-9edf-d1e53a689538', 'patch', 'alice', 6, 404, {'code': 'ICE'},
                '{"detail": "Result qualifier not found."}'
        ),
        (  # Test PATCH Result Qualifier as an anonymous user.
                'result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 'patch', 'anonymous', 6, 401, {'code': 'ICE'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Result Qualifier as an owner.
                'result-qualifiers/385e9c78-7618-453a-b8a0-6b4e927e6ae7', 'patch', 'alice', 6, 203, {'code': 'ICE'},
                '{"id": "385e9c78-7618-453a-b8a0-6b4e927e6ae7", "code": "ICE", "description": "Ice formed on the sensor.", "owner": "alice@example.com"}'
        ),
        (  # Test PATCH Sensor as a non-owner.
                'sensors/c45c6050-dc52-4a37-a562-66816a6ef1b5', 'patch', 'alice', 6, 404, {'name': 'Sensor'},
                '{"detail": "Sensor not found."}'
        ),
        (  # Test PATCH Sensor as an anonymous user.
                'sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 'patch', 'anonymous', 6, 401, {'name': 'Sensor'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Sensor as an owner.
                'sensors/a9e79b5a-ae38-4314-abb0-604ee8d6049c', 'patch', 'alice', 6, 203, {'name': 'Sensor'},
                '{"id": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "name": "Sensor", "description": "A test sensor.", "encodingType": "application/json", "manufacturer": "Sensor Manufacturer", "model": "Sensor Model", "modelLink": "http://www.example.com/model", "methodType": "Method", "methodLink": "http://www.example.com/method", "methodCode": "METHOD", "owner": "alice@example.com"}'
        ),
        (  # Test PATCH Unit as a non-owner.
                'units/a1695fce-bbee-42eb-90da-44c951be7fbd', 'patch', 'alice', 6, 404, {'name': 'Celsius'},
                '{"detail": "Unit not found."}'
        ),
        (  # Test PATCH Unit as an anonymous user.
                'units/967944cb-903b-4f96-afba-3b9e69722f8f', 'patch', 'anonymous', 6, 401, {'name': 'Celsius'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Unit as an owner.
                'units/967944cb-903b-4f96-afba-3b9e69722f8f', 'patch', 'alice', 6, 203, {'name': 'Celsius'},
                '{"id": "967944cb-903b-4f96-afba-3b9e69722f8f", "name": "Celsius", "symbol": "C", "definition": "http://www.example.com/celsius", "type": "Unit", "owner": "alice@example.com"}'
        ),
        (  # Test PATCH Data Loader as a non-owner.
                'data-loaders/9bcd1dbf-eb1e-47dd-8874-f0a65f16c709', 'patch', 'alice', 6, 404, {'name': 'Alice\'s Streaming Data Loader'},
                '{"detail": "Data loader not found."}'
        ),
        (  # Test PATCH Data Loader as an anonymous user.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 'patch', 'anonymous', 6, 401, {'name': 'Alice\'s Streaming Data Loader'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Data Loader as an owner.
                'data-loaders/9d571b4b-c986-4fa8-8933-0491ddad9e0e', 'patch', 'alice', 6, 203, {'name': 'Alice\'s Streaming Data Loader'},
                '{"id": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "name": "Alice\'s Streaming Data Loader"}'
        ),
        (  # Test PATCH Data Source as a non-owner.
                'data-sources/f47a257f-8007-4a5a-86e1-19bbd6093d9b', 'patch', 'alice', 7, 404, {'name': 'Test Data Source'},
                '{"detail": "Data source not found."}'
        ),
        (  # Test PATCH Data Source as an anonymous user.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'patch', 'anonymous', 7, 401, {'name': 'Test Data Source'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test PATCH Data Source as an owner.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'patch', 'alice', 7, 203, {'name': 'Test Data Source'},
                '{"id": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "name": "Test Data Source", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}'
        ),
        (  # Test PATCH Data Source with owned Data Loader.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'patch', 'alice', 7, 203, {'dataLoaderId': '9d571b4b-c986-4fa8-8933-0491ddad9e0e'},
                '{"id": "2c95bd7c-68f7-424e-920c-bd2e0ccc7717", "name": "Test Data Source", "path": null, "link": null, "headerRow": null, "dataStartRow": null, "delimiter": null, "quoteChar": null, "interval": null, "intervalUnits": null, "crontab": null, "startTime": null, "endTime": null, "paused": false, "timestampColumn": "A", "timestampFormat": null, "timestampOffset": null, "dataLoaderId": "9d571b4b-c986-4fa8-8933-0491ddad9e0e", "dataSourceThru": null, "lastSyncSuccessful": null, "lastSyncMessage": null, "lastSynced": null, "nextSync": null}'
        ),
        (  # Test PATCH Data Source with unowned Data Loader.
                'data-sources/2c95bd7c-68f7-424e-920c-bd2e0ccc7717', 'patch', 'alice', 7, 403, {'dataLoaderId': '9bcd1dbf-eb1e-47dd-8874-f0a65f16c709'},
                '"You do not have permission to link a data source to the given data loader."'
        ),
        (  # Test PATCH Datastream.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 203, {'name': 'TSC Temperature'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "TSC Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with primary owned Thing.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 203, {'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with secondary owned Thing.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'bob', 11, 203, {'thingId': '3b7818af-eff7-4149-8517-e5cad9dc22e1'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with unowned Thing.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'bob', 11, 403, {'thingId': '5bba0397-096b-4d60-a3f0-c00f1e6e85da'},
                '"You do not have permission to link a datastream to the given thing."'
        ),
        (  # Test PATCH Datastream with owned Sensor.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 203, {'sensorId': 'a9e79b5a-ae38-4314-abb0-604ee8d6049c'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with unowned Sensor.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 403, {'sensorId': '5fbab69a-810b-4044-bfac-c40a05634c5c'},
                '"You do not have permission to link a datastream to the given sensor."'
        ),
        (  # Test PATCH Datastream with owned Processing Level.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 203, {'processingLevelId': 'f2e18666-2a5c-4f75-b83b-aebfffc6a39f'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with unowned Processing Level.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 403, {'processingLevelId': 'fac80ccb-7e0b-4b83-9d06-1e225b1cf6bd'},
                '"You do not have permission to link a datastream to the given processing level."'
        ),
        (  # Test PATCH Datastream with owned Observed Property.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 203, {'observedPropertyId': 'cda18a59-3f2c-4c09-976f-3eadc34423bb'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with unowned Observed Property.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 403, {'observedPropertyId': 'c1479bbc-3d7e-449c-ad3a-0a1c7742b460'},
                '"You do not have permission to link a datastream to the given observed property."'
        ),
        (  # Test PATCH Datastream with owned Unit.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 203, {'unitId': '967944cb-903b-4f96-afba-3b9e69722f8f'},
                '{"id": "b2529f8b-488a-4b11-b18d-7fa4eadd62cd", "name": "UWRL Temperature", "description": "Temperature measured at the UWRL.", "observationType": "http://www.opengis.net/def/observationType/OGC-OM/2.0/OM_Measurement", "sampledMedium": "Air", "noDataValue": -9999.0, "aggregationStatistic": "Continuous", "timeAggregationInterval": 1.0, "status": "Ongoing", "resultType": "Time Series", "valueCount": 2, "phenomenonBeginTime": "2024-04-01T08:00:00Z", "phenomenonEndTime": "2024-04-02T08:00:00Z", "resultBeginTime": null, "resultEndTime": null, "dataSourceId": null, "dataSourceColumn": null, "isVisible": false, "isDataVisible": false, "thingId": "3b7818af-eff7-4149-8517-e5cad9dc22e1", "sensorId": "a9e79b5a-ae38-4314-abb0-604ee8d6049c", "observedPropertyId": "cda18a59-3f2c-4c09-976f-3eadc34423bb", "processingLevelId": "f2e18666-2a5c-4f75-b83b-aebfffc6a39f", "unitId": "967944cb-903b-4f96-afba-3b9e69722f8f", "timeAggregationIntervalUnits": "minutes", "intendedTimeSpacing": null, "intendedTimeSpacingUnits": null}'
        ),
        (  # Test PATCH Datastream with unowned Unit.
                'datastreams/b2529f8b-488a-4b11-b18d-7fa4eadd62cd', 'patch', 'alice', 11, 403, {'unitId': '054ac53a-520f-4340-96f1-889ffa12874b'},
                '"You do not have permission to link a datastream to the given unit."'
        ),
        (  # Test PATCH Datastream as a non-owner.
                'datastreams/1b98de60-0386-4d98-a933-b3cd0c09d98e', 'patch', 'bob', 11, 404, {'name': 'TSC Temperature'},
                '{"detail": "Datastream not found."}'
        ),
        (  # Test PATCH Datastream as an anonymous user.
                'datastreams/1b98de60-0386-4d98-a933-b3cd0c09d98e', 'patch', 'anonymous', 11, 401, {'name': 'TSC Temperature'},
                '{"detail": "Unauthorized"}'
        ),
        (  # Test DELETE Thing as an anonymous user.
                'things/e1f18e11-4130-485b-ad67-18f7f44187f8', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Thing as a non-owner.
                'things/e1f18e11-4130-485b-ad67-18f7f44187f8', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE Thing as a secondary owner.
                'things/e1f18e11-4130-485b-ad67-18f7f44187f8', 'delete', 'bob', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Thing.
                'things/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Thing as a primary owner.
                'things/e1f18e11-4130-485b-ad67-18f7f44187f8', 'delete', 'alice', 18, 204, None, None
        ),
        (  # Test DELETE Tag as an anonymous user.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Tag as a non-owner.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE Tag of non-existent Thing.
                'things/00000000-0000-0000-0000-000000000000/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Photo.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/tags/a12526b9-00c7-4cfd-a49a-d45514e74462', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Photo as an anonymous user.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/photos/a6360259-ba57-414d-84ab-22b5c64eb78d', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Photo as a non-owner.
                'things/76dadda5-224b-4e1f-8570-e385bd482b2d/photos/a6360259-ba57-414d-84ab-22b5c64eb78d', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE Photo of non-existent Thing.
                'things/00000000-0000-0000-0000-000000000000/photos/a6360259-ba57-414d-84ab-22b5c64eb78d', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Observed Property as an anonymous user.
                'observed-properties/2f89ca87-667f-4de9-b850-715db3cbf927', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Observed Property as non-owner.
                'observed-properties/2f89ca87-667f-4de9-b850-715db3cbf927', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Observed Property.
                'observed-properties/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Observed Property Level as owner.
                'observed-properties/2f89ca87-667f-4de9-b850-715db3cbf927', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Processing Level as an anonymous user.
                'processing-levels/57d48dd3-0fc7-4127-8e34-99c4441c7b68', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Processing Level as non-owner.
                'processing-levels/57d48dd3-0fc7-4127-8e34-99c4441c7b68', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Processing Level.
                'processing-levels/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Processing Level as owner.
                'processing-levels/57d48dd3-0fc7-4127-8e34-99c4441c7b68', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Result Qualifier as an anonymous user.
                'result-qualifiers/3064f342-f614-41a7-8748-246a711e5175', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Result Qualifier as non-owner.
                'result-qualifiers/3064f342-f614-41a7-8748-246a711e5175', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Result Qualifier.
                'result-qualifiers/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Result Qualifier as owner.
                'result-qualifiers/3064f342-f614-41a7-8748-246a711e5175', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Sensor as an anonymous user.
                'sensors/a8617070-146a-4e82-8b4d-9a6563de6265', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Sensor as non-owner.
                'sensors/a8617070-146a-4e82-8b4d-9a6563de6265', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Sensor.
                'sensors/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Sensor as owner.
                'sensors/a8617070-146a-4e82-8b4d-9a6563de6265', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Unit as an anonymous user.
                'units/23bd903d-36f2-4572-b2e2-fd0a55c00498', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Unit as non-owner.
                'units/23bd903d-36f2-4572-b2e2-fd0a55c00498', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Unit.
                'units/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Unit as owner.
                'units/23bd903d-36f2-4572-b2e2-fd0a55c00498', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Data Loader as an anonymous user.
                'data-loaders/eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Data Loader as a non-owner.
                'data-loaders/eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Data Loader.
                'data-loaders/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Data Loader as owner.
                'data-loaders/eec3e0f8-8e49-4751-ae2d-4f8ce715b1bd', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Data Source as an anonymous user.
                'data-sources/91783bce-b13a-42f7-ab22-4282c6303c42', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Data Source as a non-owner.
                'data-sources/91783bce-b13a-42f7-ab22-4282c6303c42', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Data Source.
                'data-sources/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Data Source as owner.
                'data-sources/91783bce-b13a-42f7-ab22-4282c6303c42', 'delete', 'alice', 7, 204, None, None
        ),
        (  # Test DELETE Datastream as an anonymous user.
                'datastreams/22074b3e-455a-4a4b-91c3-38e6cf85557d', 'delete', 'anonymous', 7, 401, None, None
        ),
        (  # Test DELETE Datastream as a non-owner.
                'datastreams/22074b3e-455a-4a4b-91c3-38e6cf85557d', 'delete', 'carol', 7, 404, None, None
        ),
        (  # Test DELETE non-existent Datastream.
                'datastreams/00000000-0000-0000-0000-000000000000', 'delete', 'alice', 7, 404, None, None
        ),
        (  # Test DELETE Datastream as owner.
                'datastreams/22074b3e-455a-4a4b-91c3-38e6cf85557d', 'delete', 'alice', 7, 204, None, None
        )
    ]
)
@pytest.mark.django_db()
def test_data_management_api_endpoints(
        django_assert_max_num_queries, auth_headers, base_url, endpoint, method, user, max_queries,
        expected_response_code, request_body, expected_response
):
    client = Client()

    request_kwargs = {
        'path': f'{base_url}/{endpoint}',
        **auth_headers[user]
    }

    if request_body:
        request_kwargs = {**request_kwargs, 'data': json.dumps(request_body), 'content_type': 'application/json'}

    with django_assert_max_num_queries(max_queries):
        response = getattr(client, method)(**request_kwargs)

    print(response.content)

    assert response.status_code == expected_response_code

    if expected_response is not None:
        response_json = response.json()
        expected_response_json = json.loads(expected_response)

        if isinstance(response_json, list) and isinstance(expected_response_json, list):
            assert Counter(json.dumps(d, sort_keys=True) for d in response_json) == \
                   Counter(json.dumps(d, sort_keys=True) for d in expected_response_json)
        else:
            assert json.dumps(response_json, sort_keys=True) == json.dumps(expected_response_json, sort_keys=True)
