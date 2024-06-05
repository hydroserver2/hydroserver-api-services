import uuid
from datetime import datetime, timedelta
import math
import random

# def generate_point(hour):
#     day_of_year = current_time.timetuple().tm_yday
#     daily_temp = 10 * math.sin(math.pi * (hour - 3) / 12)
#     seasonal_temp = 10 * math.sin(math.pi * (day_of_year - 80) / 182.5)
#     return daily_temp + seasonal_temp + random.gauss(0, 1.5)

# def generate_point():
#     return random.uniform(0.000, 0.001)

def generate_point():
    return round(random.gauss(mu=10, sigma=1), 2)

global_RQ = None
def getResultQualifier():
    weights = [1,1,1,1]
    weights[choices.index(global_RQ)] = 5
    return random.choices(choices, weights, k = 1)[0]

def generate_observation(result):
    global_RQ = getResultQualifier()

    observation = {
        "fields": {
            "datastream": datastream_id,
            "result": result,
            "phenomenon_time": current_time.strftime('%Y-%m-%d %H:%M:%S+00:00'),
        },
        "model": "core.observation",
        "pk": str(uuid.uuid4())
    }

    if global_RQ:
        observation['fields']['result_qualifiers'] = [global_RQ]

    # observation.fields.add()
    yaml_string = "- model: {}\n".format(observation["model"])
    yaml_string += "  pk: {}\n".format(observation["pk"])
    yaml_string += "  fields:\n"
    for key, value in observation["fields"].items():
        yaml_string += "    {}: {}\n".format(key, value)
    return yaml_string


if __name__ == "__main__":
    datastream_id = str(uuid.uuid4())
    current_time = datetime.strptime("2024-06-4 10:00:00", '%Y-%m-%d %H:%M:%S')
    end_time = current_time
    
    intended_time_spacing = 15
    time_delta = timedelta(minutes=intended_time_spacing)

    output_file = 'output.yaml'
    observations = []
    num_observations = 1000

    PAUL_ICE = '565b2407-fc55-4e4a-bcd7-6e945860f11b'
    PAUL_MNT = '93ccb684-2921-49df-a6cf-2f0dea8eb210'
    PAUL_SED = '0037b570-0247-4ccf-a5f2-0831546571cf'

    choices = [PAUL_ICE, PAUL_MNT, PAUL_SED, None]

    for i in range(num_observations):
        data_point = generate_point()
        observations.append(generate_observation(data_point))
        current_time -= time_delta
    current_time += time_delta # For the last point

    start_time = current_time
    with open(output_file, 'w') as outfile:
        outfile.writelines(observations)

    print(f"File '{output_file}' generated with {num_observations} observations.")
    print(f"phenomenon_start_time = {start_time}")
    print(f"phenomenon_end_time = {end_time}")