import os
import json
import random
from locust import HttpUser, task
from datetime import datetime, timedelta


class GetThingCollection(HttpUser):

    timestamp = datetime(2023, 4, 1, 0, 0, 0)

    # @task
    def get_thing_collection(self):
        self.client.get(
            '/sensorthings/v1.1/Things',
            auth=(os.getenv('LOCUST_TEST_USERNAME'), os.getenv('LOCUST_TEST_PASSWORD'))
        )

    @task
    def post_observations(self):

        data_array = []

        for _ in range(96):
            data_array.append([
                self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                random.randint(0, 100)
            ])

            self.timestamp = self.timestamp + timedelta(minutes=15)

        request_body = [
            {
                'Datastream': {
                    '@iot.id': '376be82c-b3a1-4d96-821b-c7954b931f94'
                },
                'components': [
                    'resultTime',
                    'result'
                ],
                'dataArray': data_array
            }
        ]
