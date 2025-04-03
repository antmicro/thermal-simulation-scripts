import json
from pathlib import Path
import typer
from preprocessing.calculate_coef import calculate_film_coefficient
from preprocessing.parse_fcstd import set_coef


def main(fcstd: str, config: str):

    config_path = Path(config).resolve().as_posix()
    with open(config_path, "r") as file:
        config = json.load(file)

    for coef_name in config["film"]:
        film = calculate_film_coefficient(
            config["temperature"]["ambience"],
            config["temperature"]["max"],
            config["film"][coef_name][1],
            config["film"][coef_name][0],
        )
        set_coef(fcstd, "film", film, coef_name)


if __name__ == "__main__":
    typer.run(main)
