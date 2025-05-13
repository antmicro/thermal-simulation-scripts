from postprocessing import create_csv
from postprocessing import create_plot
from pathlib import Path
import typer
from typing import Optional
import subprocess

app = typer.Typer()


@app.command()
def csv(
    vtk: str = typer.Option("vtk", help="Path to directory with .vtk files"),
    sta: str = typer.Option(
        "FEMMeshGmsh.sta", help="Path to CalculiX time stamp file (.sta)"
    ),
    output: str = typer.Option("temperature.csv", help="Path to output file"),
):
    """Generate csv file from simulation output"""
    create_csv.main(vtk, sta, output)


@app.command()
def plot(
    csv: str = typer.Option(
        "temperature.csv", help="Path to simulation data file (.csv)"
    ),
    output: str = typer.Option("graphs", help="Path to graph directory"),
    sim: Optional[str] = typer.Option(None, help="Path to simulation settings file"),
):
    """Plot temperature vs time graphs"""
    create_plot.main(csv, output, sim)


@app.command()
def x3d():
    """Generate x3d files for every time step"""
    path = Path(__file__).parent
    subprocess.run(["pvpython", str(path / "create_x3d.py")])


@app.command()
def preview():
    """Create image previews"""
    path = Path(__file__).parent
    subprocess.run(["pvpython", str(path / "create_previews.py")])


@app.command()
def animation():
    """Create an animation"""
    path = Path(__file__).parent
    subprocess.run(["pvpython", str(path / "create_animation.py")])


def main():
    """Main script function"""
    app()


if __name__ == "__main__":
    main()
