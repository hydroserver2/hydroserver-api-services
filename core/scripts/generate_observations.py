import uuid
from datetime import datetime, timedelta
import math
import random

def generate_observation(base_time, result):
    observation = {
        "fields": {
            "datastream": "02a1c3f0-ae31-41f6-a27a-f3e7a5d8f2a3",
            "result": result,
            "phenomenon_time": base_time.strftime('%Y-%m-%d %H:%M:%S+00:00'),
            # "result_time": None,
            # "feature_of_interest": None,
            # "quality_code": None
        },
        "model": "core.observation",
        "pk": str(uuid.uuid4())
    }

    yaml_string = "- model: {}\n".format(observation["model"])
    yaml_string += "  pk: {}\n".format(observation["pk"])
    yaml_string += "  fields:\n"
    for key, value in observation["fields"].items():
        yaml_string += "    {}: {}\n".format(key, value)
    return yaml_string

def get_temperature(hour, day_of_year):
    daily_temp = 10 * math.sin(math.pi * (hour - 3) / 12)
    seasonal_temp = 10 * math.sin(math.pi * (day_of_year - 80) / 182.5)
    return daily_temp + seasonal_temp + random.gauss(0, 1.5)

observations = []
base_time = datetime.strptime("2022-03-01 10:00:10", '%Y-%m-%d %H:%M:%S')

for i in range(10000):
    day_of_year = base_time.timetuple().tm_yday
    temperature = get_temperature(base_time.hour, day_of_year)
    observations.append(generate_observation(base_time, temperature))
    base_time += timedelta(minutes=5)

with open('temperature_output.yaml', 'w') as outfile:
    outfile.writelines(observations)

print("File 'temperature_output.yaml' generated with 100,000 observations.")