import os
import subprocess
import argparse
import glob

BASE_DIR = os.path.join('core', 'fixtures', 'tests')


def split_large_file(filepath, lines_per_file=20_000):
    """
    Split a large file into smaller chunks, ensuring each chunk is valid YAML.
    Returns a list of generated filenames.
    """
    generated_files = []
    current_lines = 0
    buffer = []
    should_write = False

    with open(filepath) as bigfile:
        for line in bigfile:
            buffer.append(line)
            current_lines += 1
            if line.strip().startswith("- model:"):
                if current_lines > lines_per_file:
                    should_write = True
                    current_lines = 0  # reset for the next file

            if should_write:
                small_filename = filepath + '_part_{}.yaml'.format(len(generated_files) * lines_per_file)
                with open(small_filename, "w") as smallfile:
                    smallfile.writelines(buffer[:-1])  # Exclude the current "- model:" line
                generated_files.append(small_filename)
                print(f"Generated {small_filename}.")
                buffer = [line]  # start the buffer for the next file with the current "- model:" line
                should_write = False

        # Write remaining lines if there are any
        if buffer:
            small_filename = filepath + '_part_{}.yaml'.format(len(generated_files) * lines_per_file)
            with open(small_filename, "w") as smallfile:
                smallfile.writelines(buffer)
            generated_files.append(small_filename)
            print(f"Generated {small_filename}.")

    return generated_files


def load_data_file(filepath):
    # Check the file size, if it's above a threshold, split it
    file_size = os.path.getsize(filepath)
    threshold_size = 5 * 1024 * 1024  # example threshold of 5MB
    if file_size > threshold_size:
        print(f"Splitting {filepath} due to large size...")
        chunk_files = split_large_file(filepath)
        for chunk in chunk_files:
            load_chunk(chunk)
            os.remove(chunk)  # Optionally remove the chunk after loading
    else:
        load_chunk(filepath)


def load_chunk(filepath):
    cmd = f"python manage.py loaddata {filepath}"
    result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if result.returncode != 0:
        print(f"Failed to load {filepath}.\nError: {result.stderr.decode('utf-8')}")
    else:
        print(f"Successfully loaded {filepath}.")


def load_data_for_directory(directory_path):
    # Load thing.yaml first
    thing_path = os.path.join(directory_path, "thing.yaml")
    if os.path.exists(thing_path):
        load_data_file(thing_path)
    
    # Load all other yaml files in the directory
    for yaml_file in sorted(glob.glob(os.path.join(directory_path, "*.yaml"))):
        if yaml_file != thing_path:
            load_data_file(yaml_file)


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
