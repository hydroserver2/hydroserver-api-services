import json
from django.test import TestCase, Client
from django.conf import settings
from .utils import metadata_validator


class CreateSensorTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.sensor_data = {
            'name': 'test_sensor',
            'description': 'A test sensor.',
            'encodingType': 'application/pdf',
            'metadata': 'http://www.example.com/test.pdf'
        }
        self.request_url = f'{settings.ST_BASE_URL}/Sensors'

    def test_create_sensor(self):
        """
        Sends a POST request with a valid sensor body and tests that the response conforms to the SensorThings
        specification by returning a 201 status code and a location value in the response headers.
        """

        response = self.client.post(
            self.request_url,
            json.dumps(self.sensor_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers.get('location'), 'testserver/sta/v1.1/Sensors(1)')


class MetadataFieldValidator(TestCase):

    def test_valid_metadata(self):
        """
        Runs the metadata validator on a valid metadata value and corresponding encoding type. The validator should
        return the original value without raising a ValidationError.
        """

        raw_value = 'http://www.example.com/test.pdf'

        validated_value = metadata_validator(
            value=raw_value,
            values={
                'encoding_type': 'application/pdf'
            }
        )

        self.assertEqual(raw_value, validated_value)

    def test_invalid_metadata(self):
        """
        Runs the metadata validator on an invalid metadata value. The validator should raise a ValueError.
        """

        raw_value = 'not/a/valid/url.pdf'

        self.assertRaises(
            ValueError,
            metadata_validator,
            value=raw_value,
            values={
                'encoding_type': 'application/pdf'
            }
        )

    def test_metadata_type_mismatch(self):
        """
        Runs the metadata validator on a valid metadata value with the wrong encoding type. The validator should raise
        a ValueError.
        """

        raw_value = 'https://www.example.com/test.xml'

        self.assertRaises(
            ValueError,
            metadata_validator,
            value=raw_value,
            values={
                'encoding_type': 'application/pdf'
            }
        )
