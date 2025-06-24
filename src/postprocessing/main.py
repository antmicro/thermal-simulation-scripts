from postprocessing import create_csv
from postprocessing import create_plot
from pathlib import Path
import typer
from typing import Optional
import subprocess
import logging

app = typer.Typer()

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


@app.command()
def process_blend(
    input: str = typer.Option("raw.blend", help="Path to input blend (.blend)"),
    output: str = typer.Option("processed.blend", help="Path to output blend (.blend)"),
    material: str = typer.Option(
        "merged.blend", help="Path to file with thermal_threshold material (.blend)"
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
def merge_materials(
    lib: str = typer.Option(
        help="File containing material specified in config (.blend)"
    ),
    lib_thermal: str = typer.Option(
        default=Path(__file__).parent.resolve() / "material.blend",
        help="File containing thermal mask material (.blend)",
    ),
    config: str = typer.Option(default="config.json", help="Path to config (.json)"),
    output_material: str = typer.Option(
        default="merged.blend", help="Path to material blend file (.blend)"
    ),
):
    """Merge thermal mask with Blender library material."""
    from postprocessing import process_blend

    process_blend.merge_materials(lib, lib_thermal, config, output_material)


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
