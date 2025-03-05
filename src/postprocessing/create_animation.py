from paraview.simple import *  # type: ignore
import paraview.servermanager
from pathlib import Path
import os
import glob
import pandas as pd
import numpy as np
from enum import Enum, auto

output_path = Path.cwd()  # X3D output file


class ViewType(Enum):
    ISO = auto()
    TOP = auto()
    BOTTOM = auto()
    FRONT = auto()
    BACK = auto()
    SIDE = auto()


def get_vtk_files() -> list[str]:
    """Get list of .vtk files"""
    files = sorted([file for file in glob.glob("vtk/*.vtk")])
    return files


def set_view(view_type: ViewType, render_view: paraview.servermanager.Proxy) -> None:
    """
    Rotate view to specific view

    Keyword arguments:
    view_type -- name of the view
    render_view -- a render view object
    """
    if view_type == ViewType.ISO:
        render_view.ApplyIsometricView()
    elif view_type == ViewType.TOP:
        render_view.ResetActiveCameraToNegativeY()
    elif view_type == ViewType.BOTTOM:
        render_view.ResetActiveCameraToPositiveY()
    elif view_type == ViewType.FRONT:
        render_view.ResetActiveCameraToPositiveZ()
    elif view_type == ViewType.BACK:
        render_view.ResetActiveCameraToNegativeZ()
    elif view_type == ViewType.SIDE:
        render_view.ResetActiveCameraToPositiveX()
        render_view.AdjustRoll(-90.0)


def get_temperatures() -> tuple[float, float]:
    """Read temperatures from simulation csv file"""
    df = pd.read_csv("temperature.csv")
    t_max = np.max(df["max [K]"])
    t_min = np.min(df["min [K]"])
    return t_max, t_min


def render_views(
    views: list[ViewType],
    output_dir: str,
    render_view: paraview.servermanager.Proxy,
    idx: int,
) -> None:
    """
    Render specific view frame

    Keyword arguments:
    views -- list of views
    output_dir -- path to output dir
    render_view -- render view object
    idx -- frame number
    """
    for view in views:

        set_view(view, render_view)
        render_view.ResetCamera(False)

        layout = GetLayout()  # type: ignore [name-defined]

        layout.SetSize(2048, 2048)

        SaveScreenshot(f"{output_dir}/{view.name}_{idx:06d}.png", render_view)  # type: ignore [name-defined]


def make_previews(files: list[str]) -> None:
    """Prepare render view

    Keyword arguments:
    files -- list of vtk files
    """
    vtk_reader = LegacyVTKReader(registrationName="Simulation", FileNames=files)  # type: ignore [name-defined]

    t_max, t_min = get_temperatures()

    animation = GetAnimationScene()  # type: ignore [name-defined]

    animation.UpdateAnimationUsingDataTimeSteps()

    view = GetActiveViewOrCreate("RenderView")  # type: ignore [name-defined]

    display = Show(vtk_reader, view, "UnstructuredGridRepresentation")  # type: ignore [name-defined]
    view.ResetCamera(False)

    view.Update()

    ColorBy(display, ("POINTS", "NT"))  # type: ignore [name-defined]
    colort_fuction = GetColorTransferFunction("NT")  # type: ignore [name-defined]
    colort_fuction.RescaleTransferFunction(t_min, t_max)
    display.SetScalarBarVisibility(view, True)

    scene = GetAnimationScene()  # type: ignore [name-defined]
    end_time = int(scene.EndTime) + 1

    if not os.path.exists("animations"):
        os.makedirs("animations")

    for idx in range(0, end_time):
        animation.AnimationTime = idx
        render_views(
            [ViewType.ISO, ViewType.TOP, ViewType.BOTTOM], "animations", view, idx
        )


def main() -> None:
    """main script function"""
    paraview.simple._DisableFirstRenderCameraReset()

    files = get_vtk_files()
    make_previews(files)

    print("DONE")


main()
