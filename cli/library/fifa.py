import json
import requests

urls = {
    "womens_ranking": "https://www.fifa.com/api/ranking-overview?locale=en&dateId=ranking_20220805",
    "mens_ranking": "https://www.fifa.com/api/ranking-overview?locale=en&dateId=id13687"
}


def get_world_ranking(gender: str):
    if gender is None:
        return []

    gender = gender.strip()

    if len(gender) == 0:
        return []

    if gender not in ["male", "female", "men", "women"]:
        return []

    if gender in ["male", "men"]:
        url = urls["mens_ranking"]
    else:
        url = urls["womens_ranking"]

    headers = {
        "age": "20",
        "cache-control": "no-store",
        "content-type": "application/json; charset=utf-8",
        "date": "Fri, 05 Aug 2022 16:06:40 GMT",
        "etag": "11fcf-misYTzkmvj2qs2uNrbHjTylvJWo+ident",
        "last-modified": "Fri, 05 Aug 2022 16:06:20 GMT",
        "request-context": "appId=cid-v1:510500c9-003a-4db2-a2f1-8b386bf67e8c",
        "server": "ECAcc (agc/7F6B)",
        "vary": "Accept-Encoding",
        "x-cache": "HIT",
        "x-match-r16": "ru"       
    }

    data = {}

    response = requests.post(url, data=data, headers=headers, stream=True)
    response.raise_for_status()

    data = response.raw.read()
    print(data)

    return data

    