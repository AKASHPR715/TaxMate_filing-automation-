import json
import requests
import os

# Load extracted data
base_dir = "/home/akash.prathap@acsiatech.com/Desktop/TaxMate_filing-automation-/app/data/extracted"
data = {}

# Map files to normalized keys
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

print(f"Payload keys: {list(data.keys())}")

# Send request
try:
    response = requests.post("http://localhost:8000/api/details/calculate", json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        res = response.json()
        comp = res.get("computation_result", {})
        print(f"Optimal Regime: {comp.get('optimal_regime')}")
        print(f"New Tax: {comp.get('new_tax')}")
        print(f"Old Tax: {comp.get('old_tax')}")
    else:
        print(response.text)
except Exception as e:
    print(f"Error: {e}")
