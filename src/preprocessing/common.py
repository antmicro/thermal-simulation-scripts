import json
from pathlib import Path


def get_config(config_path: str) -> dict:
    with open(Path(config_path).resolve().as_posix(), "r") as file:
        config = json.load(file)
    return config


def save_config(data: dict, config_path: str) -> None:
    with open(Path(config_path).resolve().as_posix(), "w") as file:
        json.dump(data, file)
