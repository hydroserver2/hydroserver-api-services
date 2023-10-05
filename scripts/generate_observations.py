import uuid
from datetime import datetime, timedelta
import math
import random

def generate_observation(base_time, result):
    observation = {
        "fields": {
            "datastream": datastream_id,
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

if __name__ == "__main__":
    datastream_id = "02a1c3f0-ae31-41f6-a27a-f3e7a5d8f2a3"
    time_delta = 15
    output_file = 'temperature_output.yaml'
    base_time = datetime.strptime("2023-10-04 10:00:00", '%Y-%m-%d %H:%M:%S')
    end_time = base_time
    observations = []
    num_observations = 350_000

    for i in range(num_observations):
        day_of_year = base_time.timetuple().tm_yday
        temperature = get_temperature(base_time.hour, day_of_year)
        observations.append(generate_observation(base_time, temperature))
        base_time -= timedelta(minutes=time_delta)

    start_time = base_time
    with open(output_file, 'w') as outfile:
        outfile.writelines(observations)

    print(f"File '{output_file}' generated with {num_observations} observations.")
    print(f"phenomenon_start_time = {start_time}")
    print(f"phenomenon_end_time = {end_time}")