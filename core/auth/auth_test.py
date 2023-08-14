import requests


request_url = 'http://127.0.0.1:8000/api2/auth/google/test'

response = requests.get(
    request_url,
    auth=('kenneth.lippold@usu.edu', '8eR19np!0i')
)

print(response.content)
