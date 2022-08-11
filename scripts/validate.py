#!/usr/bin/env python3

import os
import json
import fnmatch

def get_files(root_path: str) -> list:
    file_paths = []

    for root, dir, files in os.walk(root_path):
        for items in fnmatch.filter(files, "*.json"):
            file_path = root + "/" + items
            file_paths.append(file_path)

    return file_paths


def validate_json(json_data):
    try:
        json.loads(json_data)
    except ValueError as err:
        return False
    return True


def validate_file(file_path: str):
    with open(file_path) as f:
        contents = f.read()
        
        if validate_json(contents) is False:
            print(f"There is a problem with {file_path}!")
            return False

    return True


def validate_files(file_paths: list):
    bad_count = 0
    for file_path in file_paths:
        result = validate_file(file_path)
        if result is False:
            bad_count += 1

    if bad_count > 0:
        print(f"There were {bad_count} problems detected")
    else:
        print("GOOD TO GO!")

if __name__ == "__main__":
    file_paths = get_files("org")
    file_paths.sort()
    validate_files(file_paths)
