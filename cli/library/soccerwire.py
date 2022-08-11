from fnmatch import translate
from pprint import pprint
from urllib.error import HTTPError

import json
import requests

from bs4 import BeautifulSoup

from common import config
from . import topdrawer as topdrawer_library

PREFIX = "https://www.soccerwire.com"

urls = {
    "commitments": "https://www.soccerwire.com/wp-json/v1/elastic-proxy/soccerwirecom-post-1/_search"
}

class SoccerWireController:
    def __init__(self):
        """Something"""
        pass

    def get_url(self, gender, year):
        if gender == "male":
            if year == "2020":
                return "https://www.soccerwire.com/recruiting/boys-2020"
            elif year == "2022":
                return "https://www.soccerwire.com/recruiting/boys-2022-college-commitments/?filter=eyJzb3J0X2J5IjoibWV0YS5pc19mZWF0dXJlZC5yYXciLCJzb3J0X2RpcmVjdGlvbiI6ImRlc2MiLCJxdWVyeSI6IiIsInNlbGVjdGVkRmlsdGVycyI6eyJtZXRhLmdlbmRlci5yYXciOiJtYWxlIiwibWV0YS5ncmFkdWF0aW9uX3llYXIucmF3IjoiMjAyMiIsIm1ldGEuaXNfY29tbWl0dGVkLnJhdyI6IjEifSwic2VsZWN0ZWRSYW5nZUZpbHRlcnMiOnt9LCJjdXJyZW50UGFnZSI6MX0="
            else:
                return f"https://www.soccerwire.com/boys-{year}-college-commitments"
        elif gender == "female":
            if year == "2020":
                return "https://www.soccerwire.com/recruiting/girls-2020-college-commitments"
            elif year == "2021":
                return "https://www.soccerwire.com/recruiting/girls-2021-college-commitments"
            else:
                return f"https://www.soccerwire.com/girls-{year}-college-commitments"
        else:
            return None


    def commitments(self, gender, year, team=None, club=None, positions=None, state=None):
        url = self.get_url(gender, year)

        response = requests.get(url)

        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        table = soup.find("table", {"id": "players__table"})
        body = table.find("tbody")
        rows = body.find_all("tr")

        if table is None:
            print("Unable to locate the table")



        print(f"Gender {gender}")
        print(f"Year {year}")
        print(f"Team {team}")
        print(f"Club {club}")
        print(f"Positions {positions}")
        print(f"State {state}")

        return []

def _build_commitments_payload(gender: str, year: str, size: int = 0):
    return {
        "size": size,
        "post_filter": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "post_type.raw": "players"
                        }
                    },
                    {
                        "term": {
                            "post_status": "publish"
                        }
                    },
                    {
                        "term": {
                            "meta.gender.raw": gender
                        }
                    },
                    {
                        "term": {
                            "meta.graduation_year.raw": year
                        }
                    },
                    {
                        "term": {
                            "meta.is_committed.raw": "1"
                        }
                    }
                ],
                "must_not": []
            }
        },
        "sort": [
            {
                "meta.is_featured.raw": "desc"
            }
        ],
        "query": {
            "function_score": {
                "query": {
                    "multi_match": {
                        "query": "",
                        "operator": "and",
                        "boost": 1,
                        "fuzziness": 1,
                        "prefix_length": 0,
                        "max_expansions": 100
                    }
                }
            }
        },
        "from": 0
    }


def _get_number_of_commitments(gender: str, year: str):
    """Retrieve the total number of commitments for a given gender and year."""
    url = urls["commitments"]

    response = requests.post(url, json=_build_commitments_payload(gender, year, 0))
    data = response.json()

    count = data["hits"]["total"]

    return count


def _get_player_league(player, default="Other"):
    club = _get_player_club(player, None)

    if club is not None:
        league = topdrawer_library._get_league(club)

        if league == "Other":
            league = _get_custom_property(player, "league_title", default)
            league = _translate_league(league)
    else:
        league = _get_custom_property(player, "league_title")
        league = _translate_league(league)

    return league


def _translate_league(league: str):
    if league == "US Youth Soccer National League P.R.O.":
        return "National League PRO"

    if league == "US Youth Soccer National League":
        return "National League"

    if league == "Elite Clubs National League (ECNL)":
        return "ECNL"

    if league == "ECNL Regional Leagues":
        return "ECRL"

    if league == "Girls Academy":
        return "GA"

    return league


def _translate_commitment(commitment: str):
    if commitment is None:
        return None

    commitment = commitment.strip()
    commitment = commitment.replace(" Women", "")
    commitment = commitment.replace(" Men", "")

    return commitment

def _get_root_property(player, key: str, default = None):
    if player is None:
        return default

    if key is None:
        return default

    key = key.strip()

    if len(key) == 0:
        return default

    if key not in player:
        return default

    return player[key]

def _get_property(player, identifier: str, key: str, default = None):
    if player is None:
        return default

    if key is None:
        return default

    key = key.strip()
    if len(key) == 0:
        return default

    if identifier not in player:
        return default

    if key not in player[identifier]:
        return default

    collection = player[identifier][key]

    if collection is None:
        return default

    if len(collection) < 1:
        return default # This may need to change in the case where there are multiple values.

    item = collection[0]
    if "value" not in item:
        return default

    value = item["value"]
    if value is None:
        if "raw" not in item:
            return default

        value = item["raw"]

        if value is None:
            return default

    value = value.strip()

    if len(value) == 0:
        value = None

    return value


def _get_meta_property(player, key: str, default = None):
    return _get_property(player, "meta", key, default)

def _get_custom_property(player, key: str, default = None):
    if player is None:
        return default

    if key is None:
        return default

    key = key.strip()
    if len(key) == 0:
        return default

    if "custom_fields" not in player:
        return default

    if key not in player["custom_fields"]:
        return default

    value = player["custom_fields"][key]

    if value is None:
        return default

    if type(value) is not str:
        return default

    value = value.strip()

    return value


def _get_player_position(player, default = None):
    if player is None:
        return default

    if "meta" not in player:
        return default

    if "positions" not in player["meta"]:
        return default

    collection = player["meta"]["positions"]

    if collection is None:
        return default

    if len(collection) < 1:
        return default # This may need to change in the case where there are multiple values.

    item = collection[0]
    if "raw" not in item:
        return default

    raw = item["raw"]
    raw = raw.strip()

    return raw

def _get_player_club(player, default = None):
    club = _get_custom_property(player, "club_title", default)
    club = config.translate_club_name(club)

    return club

def _get_player_commitment(player, default = None):
    if player is None:
        return default

    commitment = _get_custom_property(player, "college_team", default)
    commitment = _translate_commitment(commitment)

    return commitment

def _get_player_commitment_url(player, default = None):
    if player is None:
        return default

    url = _get_custom_property(player, "college_link", default)

    return url

def _get_player_city(player, default = None):
    city = _get_meta_property(player, "birthplace_city", None)

    if city is None:
        return default

    city = city.strip()
    if len(city) == 0:
        return default

    return city

def _translate_player(player):
    translated_player = {}
    translated_player["id"] = _get_root_property(player, "ID", None)
    translated_player["name"] = _get_root_property(player, "post_title", None)
    translated_player["url"] = _get_root_property(player, "permalink", None)
    translated_player["imageUrl"] = _get_meta_property(player, "image", None)
    translated_player["position"] = _get_player_position(player, None)
    translated_player["club"] = _get_player_club(player, None)
    translated_player["league"] = _get_player_league(player, "Other")
    translated_player["highSchool"] = _get_meta_property(player, "high_school", None)
    translated_player["rating"] = _get_meta_property(player, "rating_player", None)
    translated_player["year"] = int(_get_meta_property(player, "graduation_year", None))
    translated_player["city"] = _get_player_city(player, None)
    translated_player["state"] = _get_meta_property(player, "state_province", None)
    translated_player["commitment"] = _get_player_commitment(player, None)
    translated_player["commitmentUrl"] = _get_player_commitment_url(player, None)

    return translated_player


def get_commitments(gender: str, year: int):
    """Retrieve all of the commitments for a given gender and year."""
    url = urls["commitments"]

    gender = gender.strip().lower()

    total = _get_number_of_commitments(gender, year)
    response = requests.post(url, json=_build_commitments_payload(gender, year, total))
    data = response.json()

    # Output the Soccerwire players for debugging purposes.
    # json_object = json.dumps(data["hits"]["hits"], indent=4)
    # with open("commitments.json", "w") as outfile:
    #     outfile.write(json_object)

    players = []
    for item in data["hits"]["hits"]:
        player = item["_source"]
        # print(f"Translating '{item['_source']['post_title']}' ...")
        translated_player = _translate_player(player)

        # print(f"Successfully translated '{translated_player['name']}'")

        players.append(translated_player)

    return players
