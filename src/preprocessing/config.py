import json
from pathlib import Path
import logging
import csv


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

    for coef_name in config["film"]:
        film = calculate_film_coefficient(
            config["temperature"]["ambience"],
            config["temperature"]["max"],
            config["film"][coef_name][1],
            config["film"][coef_name][0],
        )
        set_coef(fcstd, "film", film, coef_name)
        logging.info(f"Set {coef_name} to {film}")


def compare_config(config:str, csv_path:str):

    # Get simulation temp
    p = Path(csv_path).resolve().as_posix()
    with open(p, "r") as file:
        csv_reader = csv.DictReader(file)
        max_sim_temp:float = 0
        for row in csv_reader:
            value = float(row['max [C]'])
            if max_sim_temp == 0 or value > max_sim_temp:
                max_sim_temp = value

    # Get config temp
    config_path = Path(config).resolve().as_posix()
    with open(config_path, "r") as file:
        config = json.load(file)
    max_config_temp = config["temperature"]["max"]
    min_config_temp = config["temperature"]["min"]

    # Check boundry conditions
    if max_sim_temp > max_config_temp or max_sim_temp < min_config_temp:
        raise Exception(f"Simulated temperature {max_sim_temp} is outside config temp {min_config_temp},{max_config_temp}")

    logging.info(f"Sim temp is {max_sim_temp} and config temp is {max_config_temp}")






    
