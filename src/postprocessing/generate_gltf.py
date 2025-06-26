import paraview.simple as pvs
import glob
from pathlib import Path
import os

output_path = Path.cwd()


def ensure_output_directory(directory: str) -> None:
    """Ensure that the specified directory exists."""
    os.makedirs(directory, exist_ok=True)


def get_vtk_files() -> list[str]:
    """Get list of .vtk files."""
    files = sorted([file for file in glob.glob("vtk/*.vtk")])
    return files


def temperature_displayer(input_data, input_viewer, tmin, tmax):
    # Create LUT
    temperatureLUT = pvs.GetColorTransferFunction("NT")
    temperatureLUT.ScalarRangeInitialized = 1.0
    temperatureLUT.ApplyPreset("X Ray", True)
    temperatureLUT.AutomaticRescaleRangeMode = "Never"
    temperatureLUT.RescaleTransferFunction(tmin, tmax)
    # Create display
    temperature_display = pvs.Show(
        input_data, input_viewer, "UnstructuredGridRepresentation"
    )
    temperature_display.ColorArrayName = ["POINTS", "NT"]
    temperature_display.LookupTable = temperatureLUT
    temperature_display.SetScalarBarVisibility(input_viewer, True)
    temperature_display.RescaleTransferFunctionToDataRange = 0
    return temperature_display


def generate(
    output_dir: str = "gltf", t_min: float = 273.15, t_max: float = 423.15
) -> None:
    ensure_output_directory(output_dir)
    files = get_vtk_files()
    print("Generating GLTF files...")
    for idx, file in enumerate(files):
        vtk_reader = pvs.OpenDataFile(file)
        render_view = pvs.GetActiveViewOrCreate("RenderView")
        display = temperature_displayer(vtk_reader, render_view, 273.15, 433.15)
        pvs.UpdatePipeline()
        pvs.Render()
        filename = f"{output_dir}/{idx:04d}.gltf"
        pvs.ExportView(filename, view=render_view)
        pvs.Delete(vtk_reader)
        pvs.Delete(display)
    print("Finished")


if __name__ == "__main__":
    generate()
