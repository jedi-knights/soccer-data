import json
from multiprocessing import process
from urllib import request
from timeit import default_timer as timer
from datetime import timedelta
import requests


def load_club_translations(path: str):
    translations = {}

    f = open(path)
    container = json.load(f)

    for translation in container["data"]:
        translations[translation["from"]] = translation["to"]

    f.close()

    return translations


def load_ga_clubs(path: str):
    f = open(path)
    container = json.load(f)

    clubs = container["data"]

    f.close()

    return clubs 


def load_github_data(url):
    response = requests.get(url)
    response.raise_for_status()

    try:
        json_response = response.json()
    except Exception as err:
        print(err)

    return json_response["data"] 


def process_github_list():
    start = timer()
    print("Loading GitHub Data ...")
    data = {}

    f = open("cli/data/github_data.lst", "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        line = line.strip()
        if len(line) == 0:
            continue

        tokens = line.split(",")
        path = tokens[0]
        url = tokens[1]

        if path[-1] == "/":
            path = path[:-1]

        tokens = path.split("/")
        pointer = data
        depth = 0
        for token in tokens:
            depth += 1

            if depth == len(tokens):
                # We are at the end of the path so we need
                # to load it here
                pointer[token] = load_github_data(url)
            else:
                if token not in pointer:
                    pointer[token] = {}

            pointer = pointer[token]

    end = timer()
    print(timedelta(seconds=end-start))
    print("Done Loading GitHub Data ...")

    return data


def translate_club_name(club_name: str):
    if club_name is None:
        return None

    club_name = club_name.strip()

    if len(club_name) == 0:
        return ''

    club_translations = load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/club_translations.json")

    for mapping in club_translations:
        if mapping["from"] == club_name:
            return mapping["to"]

    return club_name

def translate_conference_name(conference_name: str):
    if conference_name is None:
        return None

    conference_name = conference_name.strip()

    if len(conference_name) == 0:
        return ''

    club_translations = load_github_data("https://raw.githubusercontent.com/ocrosby/soccer-data/main/org/conference_translations.json")

    for mapping in club_translations:
        if mapping["from"] == conference_name:
            print(f'Translating conference from "{mapping["from"]}" to "{mapping["to"]}" ...')
            return mapping["to"]

    return conference_name


# GITHUB_DATA = process_github_list()


# DIVISION_MAPPING = GITHUB_DATA["Division Mapping"]
# POSITION_LOOKUP = GITHUB_DATA["Position Lookup"]
# REGION_LOOKUP = GITHUB_DATA["Region Lookup"]
# STATE_LOOKUP = GITHUB_DATA["State Lookup"]

# GA_CLUBS = GITHUB_DATA["GA"]["Clubs"]
# ECNL_CLUBS = GITHUB_DATA["ECNL"]["Clubs"]
# CLUB_TRANSLATIONS = GITHUB_DATA["Club Translations"]


# COLLEGE_ORGANIZATIONS = GITHUB_DATA["College"]["Organizations"]

COLLEGE_DIVISIONS = [
    {"divisionId": 1, "divisionName": "di", "orgId": "ncaa"},
    {"divisionId": 2, "divisionName": "dii", "orgId": "ncaa"},
    {"divisionId": 3, "divisionName": "diii", "orgId": "ncaa"},
    {"divisionId": 4, "divisionName": "naia", "orgId": "naia"},
    {"divisionId": 5, "divisionName": "njcaa", "orgId": "njcaa"},
]

# DEBUGGING TRANSLATIONS
# needle="Eclipse Select (IL)"
# output = translate_club_name(needle)

# print(f"'{needle}' translated to '{output}'")
# print("Done")