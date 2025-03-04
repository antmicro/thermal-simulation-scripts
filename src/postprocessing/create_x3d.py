from paraview.simple import *
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import os

output_path = Path.cwd()  # X3D output file


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


def render() -> None:
    """Render and save animation data"""
    if not os.path.exists("x3d"):
        os.makedirs("x3d")

    scene = GetAnimationScene()  # type: ignore [name-defined]
    scene_count = int(scene.EndTime) + 1

    for scene_id in range(0, scene_count):
        print(f"Exporting {scene_id} of {scene_count}")
        scene.AnimationTime = scene_id
        source = GetActiveSource()  # type: ignore [name-defined]
        view = GetActiveViewOrCreate("RenderView")  # type: ignore [name-defined]

        display = GetDisplayProperties(source, view=view)  # type: ignore [name-defined]
        ExportView(f"{output_path}/x3d/{scene_id:04d}.x3d", view=view)  # type: ignore [name-defined]


def prepare(files: list[str]) -> None:
    """Prepare render view

    Keyword arguments:
    files -- list of vtk files
    """
    vtk_reader = LegacyVTKReader(registrationName="Simulation", FileNames=files)  # type: ignore [name-defined]
    t_max, t_min = get_temperatures()
    source = GetActiveSource()  # type: ignore [name-defined]
    SetActiveSource(source)  # type: ignore [name-defined]

    render_view = GetActiveViewOrCreate("RenderView")  # type: ignore [name-defined]
    display = Show(source, render_view, "UnstructuredGridRepresentation")  # type: ignore [name-defined]

    ColorBy(display, ("POINTS", "NT"))  # type: ignore [name-defined]
    display.SetScalarBarVisibility(render_view, True)
    colort_fuction = GetColorTransferFunction("NT")  # type: ignore [name-defined]
    colort_fuction.RescaleTransferFunction(t_min, t_max)

    animationScene = GetAnimationScene()  # type: ignore [name-defined]
    animationScene.UpdateAnimationUsingDataTimeSteps()

    render_view.ResetCamera(False)
    display = Show(vtk_reader, render_view, "UnstructuredGridRepresentation")  # type: ignore [name-defined]


def main() -> None:
    """main script function"""
    paraview.simple._DisableFirstRenderCameraReset()  # type: ignore [name-defined]

    files = get_vtk_files()
    prepare(files)
    render()
    print("DONE")


main()
