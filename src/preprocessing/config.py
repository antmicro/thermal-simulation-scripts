import json
from pathlib import Path
import logging
import csv
import sys
import os

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def bisect_temperature(config_path: str, csv_path: str, bisect_csv: str):
    """
    Checks simulation output temperature.
    Compares it with the middle value of the current temperature range.
    If no covergence update the temperature range for the next simulation
    If covergence exit with 0 code
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
    with open(Path(config_path).resolve().as_posix(), "r") as file:
        config: dict = json.load(file)

    temp_high = config["temperature"]["max"]
    temp_low = config["temperature"]["min"]
    tolerance = config["temperature"]["tolerance"]
    temp_mid = (temp_low + temp_high) / 2.0
    iteration = os.environ["ITERATION"]

    # Save results to log file
    logging.info(
        f"#{iteration} Simulated temp = {temp_sim} Calculated temp = {temp_mid}"
    )
    new_row = [iteration, temp_sim, temp_mid]
    with open(Path(bisect_csv).resolve().as_posix(), "a", newline="") as csv_file:
        writer = csv.writer(csv_file)
        if csv_file.tell() == 0:
            writer.writerow(["Iteration", "sim temp", "calc temp"])
        writer.writerow(new_row)

    # Check if in range
    try:
        if temp_sim < temp_low:
            raise Exception(
                "Simulated temperature is below the lower bound of the range. Reduce the lower limit of the range."
            )
        if temp_sim > temp_high:
            raise Exception(
                "Simulated temperature is above the upper bound of the range. Increase the upper limit of the range."
            )
    except Exception as e:
        logging.error(str(e))
        sys.exit(2)

    # Break condition
    if abs(temp_sim - temp_mid) <= tolerance:
        print(f"Finished with temp mid = {temp_mid}")
        config["bisected_temp"] = temp_mid
        with open(config_path, "w") as file:
            json.dump(config, file)
        # Exit with success
        logging.info(f"Convergence at temperature = {temp_mid}")
        sys.exit(0)

    # Continue conditions
    if temp_sim > temp_mid:
        config["temperature"]["min"] = temp_mid
    else:
        config["temperature"]["max"] = temp_mid

    logging.info(
        f'New range = [{config["temperature"]["min"]} , {config["temperature"]["max"]}]'
    )

    with open(config_path, "w") as file:
        json.dump(config, file)
    logging.info("No convergence, continuing")
    sys.exit(1)
