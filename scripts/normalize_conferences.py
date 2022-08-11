

import uuid
import json

def load_json(file_path):
    f = open(file_path)

    root = json.load(f)
    data = root["data"]

    f.close()

    return data

def save_json(dst_path, data):
    root = { "data": data }
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=4, sort_keys=True)


def normalize_conference(path_to_division):
    path_to_conferences = path_to_division + '/conferences.json'
    path_to_conferences2 = path_to_division + '/conferences2.json'

    json_data = load_json(path_to_conferences)

    new_data = []
    for item in json_data:
        print(f"Processing '{item}' in '{path_to_conferences}' ...")
        new_data.append({
            "id": str(uuid.uuid4()),
            "name": item["name"]
        })

    save_json(path_to_conferences2, new_data)


if __name__ == "__main__":
    normalize_conference("org/college/ncaa/divisions/d1")
    normalize_conference("org/college/ncaa/divisions/d2")
    normalize_conference("org/college/ncaa/divisions/d3")