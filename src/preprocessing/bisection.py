import json
from pathlib import Path
import logging
import csv
import sys
import os
from preprocessing.common import get_config, save_config

log = logging.getLogger()


def bisect_temperature(config_path: str, csv_path: str):
    """Checks simulation output temperature.

    Compares it with the middle value of the current temperature range.
    If there is no convergence, update the temperature range for the next simulation.
    If convergence exit with 0 code

    """

    # Get simulated temp
    p = Path(csv_path).resolve().as_posix()
    with open(p, "r") as file:
        csv_reader = csv.DictReader(file)
        temp_sim: float = 0
        for row in csv_reader:
            value = float(row["max [C]"])
            if temp_sim == 0 or value > temp_sim:
                temp_sim = value

    # Get config parameters
    config = get_config(config_path)
    tolerance = config["temperature"]["tolerance"]
    temp_mid = (config["temperature"]["min"] + config["temperature"]["max"]) / 2.0
    iteration = os.environ["ITERATION"]

    # Save results to log file
    logging.info(
        f"#{iteration} Simulated temp = {temp_sim} Calculated temp = {temp_mid}"
    )

    # Check if in range
    if temp_sim < float(os.environ["TMIN"]):
        logging.error(
            "Simulated temperature is below the lower bound of the range. Reduce the lower limit of the range."
        )
        sys.exit(2)
    if temp_sim > float(os.environ["TMAX"]):
        logging.error(
            "Simulated temperature is above the upper bound of the range. Increase the upper limit of the range."
        )
        sys.exit(2)  # Out of range exit code 2

    # Break condition
    if abs(temp_sim - temp_mid) <= tolerance:
        config["bisected_temp"] = temp_mid
        with open(config_path, "w") as file:
            json.dump(config, file)
        logging.info(f"CONVERGENCE T = {temp_mid}")
        sys.exit(0)  # Convergence achieved exit code 0

    # Continue conditions
    if temp_sim > temp_mid:
        config["temperature"]["min"] = temp_mid
    else:
        config["temperature"]["max"] = temp_mid
    logging.info(
        f'NO CONVERGENCE -> New range = [{config["temperature"]["min"]} , {config["temperature"]["max"]}]'
    )
    save_config(config, config_path)
    sys.exit(1)  # No convergence exit code 1
