import stools

if __name__ == "__main__":
    dir_path = "org/college/ncaa/divisions"
    
    path1 = stools.genpath(dir_path, "index.json")
    json_data = stools.load_json(path1)

    for item in json_data:
        item["id"] = stools.get_guid()

    path2 = stools.genpath(dir_path, "index.json", "2")
    stools.save_json(path2, json_data)