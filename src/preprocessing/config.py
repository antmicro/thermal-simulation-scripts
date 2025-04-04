import json
from pathlib import Path
import logging
import csv
import os


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_coef(fcstd: str, config: str):

    from preprocessing.calculate_coef import calculate_film_coefficient
    from preprocessing.parse_fcstd import set_coef

    config_path = Path(config).resolve().as_posix()
    with open(config_path, "r") as file:
        config = json.load(file)
    file.close()

    temp_mid = (config["temperature"]["max"] + config["temperature"]["min"])/2.0

    for coef_name in config["film"]:
        film = calculate_film_coefficient(
            config["temperature"]["ambience"],
            temp_mid,
            config["film"][coef_name][1],
            config["film"][coef_name][0],
        )
        set_coef(fcstd, "film", film, coef_name)
        logging.info(f"Set {coef_name} to {film}")

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

    logging.info(f"Sim temp is {temp_sim} and config temp is {temp_sim}")

    # bisect

    #END
    if abs(temp_sim - temp_mid) <= tolerance:
        print(f"Finished with temp mid = {temp_mid}")
        config["bisected_temp"] = temp_mid
        with open(config_path, "w") as file:
            json.dump(config,file)
        os.environ["BISECTED_TEMP"] = str(temp_mid)
        exit()

    #UPDATE
    if temp_sim>temp_mid:
        config["temperature"]["min"] = temp_mid
    else:
        temp_high = config["temperature"]["max"] = temp_mid

    with open(config_path, "w") as file:
            json.dump(config,file)

    

    








    
