import json
import os

base_dir = "/home/akash.prathap@acsiatech.com/Desktop/TaxMate_filing-automation-/app/data/extracted"
data = {}

for filename in os.listdir(base_dir):
    if filename.endswith(".json"):
        filepath = os.path.join(base_dir, filename)
        with open(filepath, "r") as f:
            content = json.load(f)
            
        if filename.startswith("form16a"):
            data["form16a"] = content
        elif filename.startswith("form16b"):
            data["form16b"] = content
        elif filename.startswith("ais"):
            data["ais"] = content

with open("payload.json", "w") as f:
    json.dump(data, f)
