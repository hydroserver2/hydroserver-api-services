import os
import subprocess
import argparse
import glob

BASE_DIR = os.path.join('core', 'fixtures', 'tests')

def load_data_for_directory(directory_path):
    # Load thing.yaml first
    thing_path = os.path.join(directory_path, "thing.yaml")
    if os.path.exists(thing_path):
        load_data_file(thing_path)
    
    # Load all other yaml files in the directory
    for yaml_file in sorted(glob.glob(os.path.join(directory_path, "*.yaml"))):
        if yaml_file != thing_path:
            load_data_file(yaml_file)

def load_data_file(filepath):
    cmd = f"python manage.py loaddata {filepath}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print(f"Failed to load {filepath}.\nError: {result.stderr.decode('utf-8')}")
    else:
        print(f"Successfully loaded {filepath}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load data for tests.")
    parser.add_argument("--tests", nargs="*", default=[], help="Names of tests (locations) for which to load data. Loads for all tests if not specified.")
    args = parser.parse_args()

    # Load data from the people directory
    load_data_for_directory(os.path.join(BASE_DIR, "people"))

    # Load data from specified tests or all tests
    test_directories = args.tests if args.tests else os.listdir(BASE_DIR)
    
    for test_dir in test_directories:
        test_dir_path = os.path.join(BASE_DIR, test_dir)
        if os.path.isdir(test_dir_path) and test_dir != "people":  # Skip the 'people' directory
            load_data_for_directory(test_dir_path)