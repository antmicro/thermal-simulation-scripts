import preprocessing.get_settings as gs
import preprocessing.prepare as pp
import preprocessing.report as rp
import preprocessing.config as cf
import preprocessing.calculate_coef as cc
import typer
from typing_extensions import Annotated


app = typer.Typer()


@app.command(help="Generate report.md")
def report(
    sim_file: str = typer.Argument("", help="Path to simulation settings file (.json)"),
    report_dir: str = typer.Argument("", help="Path to report directory"),
):
    rp.main(sim_file, report_dir)


@app.command(help="Update simulation.json with .inp parameters")
def get_settings(
    filename: str = typer.Argument("", help="Path to simulation input file (.inp)"),
    output_file: str = typer.Argument("", help="Path to simulation output file"),
):
    """Get settings from simulation"""
    gs.main(filename, output_file)


@app.command(help="Set .inp parameters")
def prepare(
    filename: str = typer.Argument("", help="Path to simulation input file (.inp)"),
    nt_hfl_only: bool = typer.Argument(
        "", help="Simulate only structural temperature and heat flux"
    ),
):
    """Prepare simulation"""
    pp.main(filename, nt_hfl_only)


@app.command(help="Generate .inp file and save simulation parameters in .json")
def parse_fcstd(
    fcstd: str = typer.Argument("", help="Path to freecad design file (.fcstd)"),
    inp: str = typer.Argument("", help="Path to simulation input file (.inp)"),
    log: str = typer.Argument("", help="Path to simulation log file (.json)"),
):
    import preprocessing.parse_fcstd as pf

    pf.main(fcstd, inp, log)


@app.command(help="Calculate the film coefficient")
def calc_coef(
    temp_fluid: Annotated[float, typer.Argument(help="Ambient fluid temperature [*C]")],
    temp_surface: Annotated[
        float, typer.Argument(help="Estimated surface temperature [*C]")
    ],
    orientation: Annotated[
        str,
        typer.Argument(
            help="Plane orientation - either 'vertical', 'horizontal_up', 'horizontal_down'"
        ),
    ],
    length: Annotated[float, typer.Argument(help="Characteristic length [mm]")],
):
    coef = cc.calculate_film_coefficient(temp_fluid, temp_surface, orientation, length)
    print(f"Film coefficient = {coef}")


@app.command(help="Set all HeatFlux constraints to given type and value")
def set_coef(
    fcstd: Annotated[str, typer.Argument(help="FCStd file path")],
    coef_type: Annotated[
        str,
        typer.Argument(help="Coefficient type: ['film','emissivity']"),
    ],
    coef_value: Annotated[
        float,
        typer.Argument(help="Coefficient value - film[W/m^2/K] or emissivity[ratio])"),
    ],
    name: str = typer.Option(
        "", help="Change only the heat flux constraint with the given name"
    ),
):
    import preprocessing.parse_fcstd as pf

    pf.set_coef(fcstd, coef_type, coef_value, name)


@app.command(help="Calculate film coefficients and save them to .FCStd")
def get_coef(
    fcstd: Annotated[str, typer.Argument(help="FCStd file path")],
    config: Annotated[str, typer.Argument(help="Config file path")],
):
    import preprocessing.parse_fcstd as pf

    pf.get_coef(fcstd, config)


@app.command(help="Update temperature boundaries in config file")
def bisect_temperature(
    config: Annotated[str, typer.Argument(help="Config file path")],
    csv: Annotated[str, typer.Argument(help="CSV file path")],
    bisect_csv: Annotated[
        str, typer.Argument(help="Bisection algorithm .csv file path")
    ],
):
    cf.bisect_temperature(config, csv, bisect_csv)


def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
