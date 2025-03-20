import preprocessing.get_settings as gs
import preprocessing.prepare as pp
import preprocessing.report as rp


import typer


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


@app.command()
def set_coef(
    fcstd: str = typer.Option("", help="Path to input freecad design file (.fcstd)"),
    coef_type: str = typer.Option(
        "", help="Coefficient type", show_choices=["film", "emissivity"]
    ),
    coef_value: float = typer.Option(
        "", help="Coefficient value film[W/m^2/K]  or emissivity[ratio])"
    ),
):
    import preprocessing.set_coef as sc

    sc.main(fcstd, coef_type, coef_value)


def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
