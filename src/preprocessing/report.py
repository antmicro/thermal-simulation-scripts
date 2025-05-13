import typer
import json
from pathlib import Path


def generate_markdown(report_path: Path, sim_data: dict, config_data: dict) -> None:
    with open(report_path / "README.md", "w") as f:
        f.write("### Simulation settings:\n\n")
        for key, value in sim_data.items():
            if isinstance(value, dict):
                f.write(f"#### {key}:\n\n")
                for k, v in value.items():
                    f.write(f"* {k}: {v}\n")
                f.write("\n")

        for key, value in sim_data.items():
            if not isinstance(value, dict):
                if isinstance(value, str):
                    f.write(f"{key.lower()}: {value.lower()}\n\n")
                else:
                    f.write(f"{key.lower()}: {value}\n\n")

        for key, value in config_data.items():
            if key != "user_comments":
                continue
            f.write("### User comments:\n\n")
            if isinstance(value, dict):
                for k, v in value.items():
                    f.write(f"* {k}: {v}\n")
        f.write("\n\n")


def main(sim_file: str, config_file: str, report_dir: str) -> None:
    sim_file_path = Path(sim_file).resolve()
    report_path = Path(report_dir).resolve()
    config_file_path = Path(config_file).resolve()

    with open(config_file_path, "r") as f:
        config_data = json.load(f)

    with open(sim_file_path, "r") as f:
        sim_data = json.load(f)

    generate_markdown(report_path, sim_data, config_data)


if __name__ == "__main__":
    typer.run(main)
