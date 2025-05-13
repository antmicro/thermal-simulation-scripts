from preprocessing import report as report_parameters
from preprocessing import bisection
from preprocessing import calculate_coef
import typer
from typing_extensions import Annotated
from typing import Optional
from enum import Enum
import logging

app = typer.Typer()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


@app.command(help="Generate report.md")
def report(
    sim: str = typer.Option(
        "simulation.json", help="Path to simulation settings file (.json)"
    ),
    config: str = typer.Option(
        "config.json",
        help="Path to simulation config file (config.json)",
    ),
    report_dir: str = typer.Option(".", help="Path to report directory"),
):

    report_parameters.main(sim, config, report_dir)


@app.command(help="Generate .inp file and save simulation parameters in .json")
def parse_fcstd(
    fcstd: str = typer.Option(..., help="Path to freecad design file (.fcstd)"),
    inp: str = typer.Option(".", help="Path to simulation input file (.inp)"),
    log: str = typer.Option(".", help="Path to simulation log file (.json)"),
):
    from preprocessing import parse_fcstd

    parse_fcstd.main(fcstd, inp, log)


class Orientation(str, Enum):
    vertical = "vertical"
    horizontal_up = "horizontal_up"
    horizontal_down = "horizontal_down"


@app.command(help="Calculate the film coefficient")
def calc_coef(
    orientation: Annotated[Orientation, typer.Option(..., help="Surface orientation")],
    temp_fluid: float = typer.Option(..., help="Ambient fluid temperature [°C]"),
    temp_surface: float = typer.Option(..., help="Estimated surface temperature [°C]"),
    length: float = typer.Option(..., help="Characteristic length [mm]"),
):
    coef = calculate_coef.calculate_film_coefficient(
        temp_fluid, temp_surface, orientation, length
    )
    logging.info(f"Film coefficient = {coef}")


class Coefficient(str, Enum):
    film = "film"
    emissivity = "emissivity"


@app.command(help="Set all HeatFlux constraints to given type and value")
def set_coef(
    type: Annotated[Coefficient, typer.Option(..., help="Coefficient type")],
    fcstd: str = typer.Option(..., help="FCStd file path"),
    value: float = typer.Option(
        ..., help="Coefficient value - film[W/m^2/K] or emissivity[ratio])"
    ),
    name: Optional[str] = typer.Option(
        None, help="Change only the heat flux constraint with the given name"
    ),
):
    from preprocessing import parse_fcstd

    parse_fcstd.set_coef(fcstd, type, value, name)


@app.command(help="Calculate film coefficients and save them to .FCStd")
def calc_film_coefs(
    fcstd: str = typer.Option(..., help="FCStd file path"),
    config: str = typer.Option("config.json", help="Config file path (.json)"),
):
    from preprocessing import parse_fcstd

    parse_fcstd.calc_film_coefs(fcstd, config)


@app.command(help="Update temperature boundaries in config file")
def bisect_temperature(
    config: str = typer.Option("config.json", help="Config file path (.json)"),
    csv: str = typer.Option("temperature.csv", help="CSV file path"),
):
    bisection.bisect_temperature(config, csv)


def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
