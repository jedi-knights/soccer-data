
# Python program to read
# json file
  
import uuid
import json
  

if __name__ == "__main__":
# Opening JSON file
    f = open('org/ecnl/clubs.json')
    
    # returns JSON object as 
    # a dictionary
    root = json.load(f)
    data = root["data"]
    
    # Iterating through the json
    # list
    index = 1
    for item in data:
        item["id"] = str(uuid.uuid4())
        item["url"] = None
        item["conference"] = None
        item["tgs_id_str"] = str(item["tgs_id"])
    
    # Closing file
    f.close()

    with open("org/ecnl/clubs2.json", "w", encoding="utf-8") as f:
        json.dump(root, f, ensure_ascii=False, indent=4, sort_keys=True)