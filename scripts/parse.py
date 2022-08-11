import os
import json 

from pprint import pprint

if __name__ == "__main__":
    directory = os.getcwd()

    print(f"The current directory is {directory}")

    junk = []

    f = open("temp/data.txt", "r")
    for x in f:
        x = x.strip()
        tokens = x.split("\t")
        
        junk.append({
            "name": tokens[0].strip().replace("  ", " "),
            "url": tokens[1].strip().replace("  ", " ")
        })
    f.close()

    with open("temp/data.json", "w", encoding="utf-8") as f:
        json.dump(junk, f, ensure_ascii=False, indent=4, sort_keys=True)

