import preprocessing.get_settings as gs
import preprocessing.prepare as pp
import preprocessing.report as rp
import preprocessing.config as cf
import typer
from typing_extensions import Annotated


app = typer.Typer()


@app.command()
def report(
    sim_file: str = typer.Argument("", help="Path to simulation settings file (.json)"),
    report_dir: str = typer.Argument("", help="Path to raport directory"),
):
    rp.main(sim_file, report_dir)


@app.command()
def get_settings(
    filename: str = typer.Argument("", help="Path to simulation input file (.inp)"),
    output_file: str = typer.Argument("", help="Path to simulation output file"),
):
    """Get settings from simulation"""
    gs.main(filename, output_file)


@app.command()
def prepare(
    filename: str = typer.Argument("", help="Path to simulation input file (.inp)"),
    nt_hfl_only: bool = typer.Argument(
        "", help="Simulate only structural temperature and heat flux"
    ),
):
    """Prepare simulation"""
    pp.main(filename, nt_hfl_only)


@app.command()
def parse_fcstd(
    fcstd: str = typer.Argument("", help="Path to freecad design file (.fcstd)"),
    inp: str = typer.Argument("", help="Path to simulation input file (.inp)"),
    log: str = typer.Argument("", help="Path to simulation log file (.json)"),
):
    import preprocessing.parse_fcstd as pf

    pf.main(fcstd, inp, log)


@app.command(
    help="Sets all HeatFlux constraints objects to a specified type and value."
)
def set_coef(
    # fcstd: str = typer.Argument(
    #     "--fcstd", help="Path to input freecad design file (.fcstd)"
    #     ),
    fcstd: Annotated[str, typer.Argument(help="fcstd path")],
    coef_type: Annotated[
        str,
        typer.Argument(help="Coefficient type", show_choices=["film", "emissivity"]),
    ],
    coef_value: Annotated[
        float,
        typer.Argument(help="Coefficient value film[W/m^2/K]  or emissivity[ratio])"),
    ],
    name: str = typer.Option(
        "", help="Only one constraint with the given name is modified"
    ),
):
    import preprocessing.parse_fcstd as pf

    pf.set_coef(fcstd, coef_type, coef_value, name)


@app.command(help="Sets film coefficients to calculated values")
def get_coef(
    fcstd: Annotated[str, typer.Argument(help="fcstd path")],
    config: Annotated[str, typer.Argument(help="config path")],
):
    cf.get_coef(fcstd, config)

@app.command(help="Compares simulation output with last iteration")
def bisect_temperature(
    config: Annotated[str, typer.Argument(help="config path")],
    csv: Annotated[str, typer.Argument(help="csv path")]
):
    cf.bisect_temperature(config,csv)

def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
