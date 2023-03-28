import os
from locust import HttpUser, task


class GetThingCollection(HttpUser):

    @task
    def get_thing_collection(self):
        self.client.get(
            '/sensorthings/v1.1/Things',
            auth=(os.getenv('LOCUST_TEST_USERNAME'), os.getenv('LOCUST_TEST_PASSWORD'))
        )
