import typer
import json
from pathlib import Path

def main(sim_file:str,raport_dir:str)-> None:
    sim_file_path=Path(sim_file).resolve()
    raport_path=Path(raport_dir).resolve()
    with open (sim_file_path,"r") as f:
        data = json.load(f)

    with open(raport_path / "README.md", "w") as f:
        f.write('## Simulation log:\n\n')
        for key, value in data.items():
            if isinstance(value,dict):
                f.write(f'### {key}:\n\n')
                for k, v in value.items():
                    f.write(f'* {k}: {v}\n')
                f.write('\n')
                    
        for key, value in data.items():
            if not isinstance(value,dict):
                if isinstance(value,str):
                    f.write(f"##### {key.lower()}: {value.lower()}\n\n")
                else:
                    f.write(f"##### {key.lower()}: {value}\n\n")

if __name__ == "__main__":
    typer.run(main)