import stools

if __name__ == "__main__":
    dir_path = "org/pro/nwsl"
    fname = "meta.json"
    
    path1 = stools.genpath(dir_path, fname)
    json_data = stools.load_json(path1)

    new_data = []
    for item in json_data:
        new_data.append({
            "id": item["id"],
            "firstName": item["firstName"],
            "lastName": item["lastName"],
            "country": item["country"],
            "countryId": item["countryId"]
        })

    path2 = stools.genpath(dir_path, fname, "2")
    stools.save_json(path2, new_data, False)