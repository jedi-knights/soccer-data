import json
import uuid

def normalize_gender(gender: str):
    if gender == "male":
        return "Male"

    if gender == "female":
        return "Female"

    return gender

def get_anchor_text(element):
    if element is None:
        return None

    anchor = element.find("a")

    if anchor is None:
        value = element.text
        value = value.strip()

        return value

    value = anchor.text
    value = value.strip()

    return value


def get_anchor_url(element, prefix=None):
    if element is None:
        return None

    anchor = element.find("a")

    if anchor is None:
        return None

    url = anchor["href"]
    url = url.strip()

    if len(url) == 0:
        return None

    if prefix is None:
        return url

    return prefix + url


def is_member_club(target_club_name: str, clubs: list):
    if target_club_name is None:
        return False

    if clubs is None:
        return False

    temp = target_club_name.strip().lower()

    if len(temp) == 0:
        return False

    for club in clubs:
        if "name" not in club:
            continue

        name = club["name"]
        if name is None:
            continue

        name = name.strip()
        name = name.lower()
        current_club_name = name

        if current_club_name == temp:
            return True

    return False


def get_guid():
    return str(uuid.uuid4())

def save_json(dst_path, data, sort_keys=True):
    root = { "data": data }
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=2, sort_keys=sort_keys)

def load_json(file_path):
    f = open(file_path)

    root = json.load(f)
    data = root["data"]

    f.close()

    return data

def genpath(directory: str, fname: str, suffix: str = None) -> str:
    path = directory
    
    if path[-1] != "/":
        path += "/"
    
    tokens = fname.split(".")

    path += tokens[0]

    if suffix is not None:
        path += suffix

    path += "."
    path += tokens[1]

    return path