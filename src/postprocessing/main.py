import postprocessing.create_csv as ccsv
import postprocessing.create_plot as cplot
import postprocessing.raport as rp
from pathlib import Path
import os
import typer
from typing import Optional

app = typer.Typer()


@app.command()
def csv(
    vtk_directory: str = typer.Argument("", help="Path to directory with .vtk files"),
    sta_file: str = typer.Argument("", help="Path to CalculiX time stamp file (.sta)"),
    output_file: str = typer.Argument("", help="Path to output file"),
):
    """Generate csv file from simulation output"""
    ccsv.main(vtk_directory, sta_file, output_file)


@app.command()
def plot(
    data_file: str = typer.Argument("", help="Path to simulation data file (.csv)"),
    output_dir: str = typer.Argument("", help="Path to graph directory"),
    simulation_json: Optional[str] = typer.Argument(
        default=None, help="Path to simulation settings file"
    ),
):
    """Plot temperature vs time graphs"""
    cplot.main(data_file, output_dir, simulation_json)

@app.command()
def raport(
    sim_file: str = typer.Argument("", help="Path to simulation settings file (.json)"),
    raport_dir: str = typer.Argument("", help="Path to raport directory"),
):
    rp.main(sim_file,raport_dir)


@app.command()
def x3d():
    """Generate x3d files for every time step"""
    path = Path(__file__).parent
    path = f"pvpython {path}/create_x3d.py"
    os.system(path)


@app.command()
def preview():
    """Create image previews"""
    path = Path(__file__).parent
    path = f"pvpython {path}/create_previews.py"
    os.system(path)


@app.command()
def animation():
    """Create an animation"""
    path = Path(__file__).parent
    path = f"pvpython {path}/create_animation.py"
    os.system(path)

def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
