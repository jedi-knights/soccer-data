import stools

if __name__ == "__main__":
    dir_path = "org/college"
    fname = "organizations.json"
    
    path1 = stools.genpath(dir_path, fname)
    json_data = stools.load_json(path1)

    new_data = []
    for item in json_data:
        new_data.append({
            "id": stools.get_guid(),
            "name": item["name"],
            "short_name": item["id"]
        })

    path2 = stools.genpath(dir_path, fname, "2")
    stools.save_json(path2, new_data)