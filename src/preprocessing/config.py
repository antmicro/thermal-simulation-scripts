import json
import pandas as pd
from pathlib import Path
import logging


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


def compare_config(config:str, csv:str):
    csv_path = Path(csv).resolve().as_posix()
    with open(csv_path, "r") as file:
        df = pd.read_csv(file)
    max_sim_temp = df["max [C]"].max()
    file.close()

    config_path = Path(config).resolve().as_posix()
    with open(config_path, "r") as file:
        config = json.load(file)
    file.close()
    max_config_temp = config["temperature"]["max"]

    logging.info(f"Sim temp is {max_sim_temp} and config temp is {max_config_temp}")




    
