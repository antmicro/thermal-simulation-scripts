from postprocessing import create_csv
from postprocessing import create_plot
from postprocessing import plot_comparison
from pathlib import Path
import typer
from typing import Optional
from enum import Enum
import subprocess
import logging

app = typer.Typer(help="Postprocessing utilities")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


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
    """Generate temperature characteristics"""
    create_plot.main(csv, output, sim)


class Position(str, Enum):
    upper_left = "upper left"
    upper_right = "upper right"
    center = "center"  # type: ignore[assignment]
    lower_left = "lower left"
    lower_right = "lower right"


@app.command()
def compare_csv(
    legend: Optional[Position] = typer.Option(None, help="Legend location"),
    time: Optional[float] = typer.Option(None, help="Max time [s]"),
    csv1: str = typer.Option("", help="Path to 1st csv"),
    csv2: str = typer.Option("", help="Path to 2nd csv"),
    label1: str = typer.Option("Simulation", help="Name of 1st plot"),
    label2: str = typer.Option("Measurements", help="Name of 2nd plot"),
    kelvin: Optional[bool] = typer.Option(False, help="Use Kelvin temperature scale"),
    fahrenheit: Optional[bool] = typer.Option(
        False, help="Use Fahrenheit temperature scale"
    ),
    name: Optional[str] = typer.Option(None, help="Graph name"),
):
    """Compare two temperature plots on a common graph"""
    plot_comparison.plot(
        legend, time, csv1, csv2, label1, label2, kelvin, fahrenheit, name
    )


@app.command()
def process_blend(
    input: str = typer.Option("raw.blend", help="Path to input blend (.blend)"),
    output: str = typer.Option("processed.blend", help="Path to output blend (.blend)"),
    material: str = typer.Option(
        Path(__file__).parent.resolve() / "material.blend",
        help="Path to file with thermal_threshold material (.blend)",
    ),
    config: str = typer.Option("config.json", help="Path to config (.json)"),
):
    """Prepare .blend for pcbooth"""
    from postprocessing import process_blend as pb

    pb.process_blend(blend_in=input, blend_out=output, material=material, config=config)


@app.command()
def gltf_to_blend(
    gltf: str = typer.Option("", help="Path to gltf file (.gltf)"),
    blend: str = typer.Option("raw.blend", help="Path to output blend (.blend)"),
):
    """Convert format from gltf to blend"""
    from postprocessing import process_blend

    process_blend.gltf_to_blend(gltf_path=gltf, blend_path=blend)


@app.command()
def preview_camera(
    gltf: str = typer.Option("", help="Input path (.gltf)"),
    blend: str = typer.Option("camera_preview.blend", help="Path to preview (.blend)"),
):
    """Create camera preview .blend"""
    from postprocessing import process_blend

    process_blend.preview_camera(gltf_path=gltf, blend_path=blend)


@app.command()
def save_camera(
    blend: str = typer.Option("camera_preview.blend", help="Path to preview (.blend)"),
    config: str = typer.Option("config.json", help="Path to config (.json)"),
):
    """Save custom camera properties from .blend to config"""
    from postprocessing import process_blend

    process_blend.save_camera_properties(blend, config)


@app.command()
def generate_gltf():
    """Generate gltf files for every time step."""
    path = Path(__file__).parent
    subprocess.run(["pvpython", str(path / "generate_gltf.py")])


@app.command()
def preview():
    """Create paraview image previews."""
    path = Path(__file__).parent
    subprocess.run(["pvpython", str(path / "create_previews.py")])


@app.command()
def animation():
    """Create paraview animation."""
    path = Path(__file__).parent
    subprocess.run(["pvpython", str(path / "create_animation.py")])


def main():
    """Main script function."""
    app()


if __name__ == "__main__":
    main()
