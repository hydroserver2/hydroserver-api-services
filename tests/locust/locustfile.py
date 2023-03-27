from locust import HttpUser, task


class GetThingCollection(HttpUser):

    @task
    def get_thing_collection(self):
        self.client.get('/sensorthings/v1.1/Things', auth=('kenneth.lippold@usu.edu', ''))
