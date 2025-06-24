import paraview.simple as pvs
import paraview.servermanager
from pathlib import Path
import os
import glob

output_path = Path.cwd()


def get_vtk_files() -> list[str]:
    """Get list of .vtk files."""
    files = sorted([file for file in glob.glob("vtk/*.vtk")])
    return files


def set_view(view_type: str, render_view: paraview.servermanager.Proxy) -> None:
    """Rotate view to specific view.

    Keyword arguments:
    view_type -- name of the view
    render_view -- a render view object
    """

    if view_type == "iso":
        render_view.ApplyIsometricView()
    if view_type == "top":
        render_view.ResetActiveCameraToNegativeY()
    if view_type == "bottom":
        render_view.ResetActiveCameraToPositiveY()
    if view_type == "front":
        render_view.ResetActiveCameraToPositiveZ()
    if view_type == "back":
        render_view.ResetActiveCameraToNegativeZ()
    if view_type == "side":
        render_view.ResetActiveCameraToPositiveX()
        render_view.AdjustRoll(-90.0)


def render_views(
    views: list[str],
    output_dir: str,
    render_view: paraview.servermanager.Proxy,
    display: paraview.servermanager.Proxy,
) -> None:
    """Render specific view.

    Keyword arguments:
    views -- list of views
    output_dir -- path to output dir
    render_view -- render view object
    display -- frame number
    """

    for view in views:
        print(f"Rendering {view}")
        set_view(view, render_view)
        render_view.ResetCamera(False)

        layout = pvs.GetLayout()

        layout.SetSize(2048, 2048)

        display.RescaleTransferFunctionToDataRange(False, True)

        pvs.SaveScreenshot(f"{output_dir}/{view}.png", render_view)


def make_previews(files: list[str]) -> None:
    """Prepare render view.

    Keyword arguments:
    files -- list of vtk files
    """
    vtk_reader = pvs.LegacyVTKReader(registrationName="Simulation", FileNames=files)

    animation = pvs.GetAnimationScene()

    animation.UpdateAnimationUsingDataTimeSteps()

    view = pvs.GetActiveViewOrCreate("RenderView")

    display = pvs.Show(vtk_reader, view, "UnstructuredGridRepresentation")
    view.ResetCamera(False)

    view.Update()

    pvs.ColorBy(display, ("POINTS", "NT"))

    display.SetScalarBarVisibility(view, True)

    scene = pvs.GetAnimationScene()
    animation.AnimationTime = int(scene.EndTime)

    if not os.path.exists("previews"):
        os.makedirs("previews")
    render_views(
        ["iso", "top", "bottom", "front", "back", "side"], "previews", view, display
    )


def main() -> None:
    """Main script function."""
    paraview.simple._DisableFirstRenderCameraReset()

    files = get_vtk_files()
    make_previews(files)

    print("DONE")


main()
