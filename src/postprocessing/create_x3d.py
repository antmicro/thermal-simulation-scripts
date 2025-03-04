import paraview.simple as pvs
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import os

output_path = Path.cwd()  # X3D output file


def ensure_output_directory(directory: str) -> None:
    """Ensure that the specified directory exists."""
    os.makedirs(directory, exist_ok=True)


def get_vtk_files() -> list[str]:
    """Get list of .vtk files"""
    files = sorted([file for file in glob.glob("vtk/*.vtk")])
    return files


def get_temperatures() -> tuple[float, float]:
    """Get maximum and minimum temperature from simulation settings"""
    df = pd.read_csv("temperature.csv")
    t_max = np.max(df["max [K]"])
    t_min = np.min(df["min [K]"])
    return t_max, t_min


def render(output_dir: str = "x3d") -> None:
    """Render and save animation data"""
    ensure_output_directory(output_dir)
    scene = pvs.GetAnimationScene()
    scene_count = int(scene.EndTime) + 1

    for scene_id in range(0, scene_count):
        print(f"Exporting {scene_id} of {scene_count}")
        scene.AnimationTime = scene_id
        view = pvs.GetActiveViewOrCreate("RenderView")

        pvs.ExportView(f"{output_dir}/{scene_id:04d}.x3d", view=view)


def prepare(files: list[str]) -> None:
    """Prepare render view

    Keyword arguments:
    files -- list of vtk files
    """
    vtk_reader = pvs.LegacyVTKReader(registrationName="Simulation", FileNames=files)
    t_max, t_min = get_temperatures()
    source = pvs.GetActiveSource()
    pvs.SetActiveSource(source)

    render_view = pvs.GetActiveViewOrCreate("RenderView")
    display = pvs.Show(vtk_reader, render_view, "UnstructuredGridRepresentation")

    pvs.ColorBy(display, ("POINTS", "NT"))
    display.SetScalarBarVisibility(render_view, True)
    colort_fuction = pvs.GetColorTransferFunction("NT")
    colort_fuction.RescaleTransferFunction(t_min, t_max)

    animationScene = pvs.GetAnimationScene()
    animationScene.UpdateAnimationUsingDataTimeSteps()

    render_view.ResetCamera(False)
    display = pvs.Show(vtk_reader, render_view, "UnstructuredGridRepresentation")


def main(output_dir: str = "x3d") -> None:
    """main script function"""
    ensure_output_directory(output_dir)
    pvs._DisableFirstRenderCameraReset()
    files = get_vtk_files()
    prepare(files)
    render()
    print("DONE")


main()
