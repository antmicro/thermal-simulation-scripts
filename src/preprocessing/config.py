import json
from pathlib import Path
import logging
import csv
import sys


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def bisect_temperature(config :str, csv_path:str):
    
    # Get simulation temp
    p = Path(csv_path).resolve().as_posix()
    with open(p, "r") as file:
        csv_reader = csv.DictReader(file)
        temp_sim:float = 0
        for row in csv_reader:
            value = float(row['max [C]'])
            if temp_sim == 0 or value > temp_sim:
                temp_sim = value

    # Get config parameters
    config_path = Path(config).resolve().as_posix()
    with open(config_path, "r") as file:
        config = json.load(file)
    temp_high = config["temperature"]["max"]
    temp_low = config["temperature"]["min"]
    tolerance = config["temperature"]["tolerance"]
    temp_mid = (temp_low + temp_high) / 2.0

    logging.info(f"Sim temp is {temp_sim} and config temp is {temp_mid}")

    # bisect

    #END
    if abs(temp_sim - temp_mid) <= tolerance:
        print(f"Finished with temp mid = {temp_mid}")
        config["bisected_temp"] = temp_mid
        with open(config_path, "w") as file:
            json.dump(config,file)
        # Exit with success
        sys.exit(0)

    #UPDATE
    if temp_sim>temp_mid:
        config["temperature"]["min"] = temp_mid
    else:
        temp_high = config["temperature"]["max"] = temp_mid

    with open(config_path, "w") as file:
            json.dump(config,file)
    # Exit without success
    sys.exit(1)

    

    








    
