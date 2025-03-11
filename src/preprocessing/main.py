import preprocessing.get_settings as gs
import preprocessing.prepare as pp
import preprocessing.raport as rp


import typer


app = typer.Typer()

@app.command()
def raport(
    sim_file: str = typer.Argument("", help="Path to simulation settings file (.json)"),
    raport_dir: str = typer.Argument("", help="Path to raport directory"),
):
    rp.main(sim_file,raport_dir)
    

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


def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
