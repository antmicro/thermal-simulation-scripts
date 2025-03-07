import typer
import json
from pathlib import Path

def flatten_json(data, parent_key='', separator=': '):
    items = []
    for key, value in data.items():
        if isinstance(value, dict):
            items.extend(flatten_json(value, key, separator=': ').items())
        else:
            items.append((key, value))
    return dict(items)

def main(sim_file:str,raport_dir:str)-> None:
    sim_file_path=Path(sim_file).resolve()
    raport_path=Path(raport_dir).resolve()
    with open (sim_file_path,"r") as f:
        data = json.load(f)

    flattened_data = flatten_json(data)

    with open(raport_path / "README.md", "w") as f:
        for key, value in flattened_data.items():
         f.write(f"{key}: {value}\n")


if __name__ == "__main__":
    typer.run(main)