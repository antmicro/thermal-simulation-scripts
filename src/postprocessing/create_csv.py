import vtkmodules.all as vtk
from vtkmodules.util import numpy_support
import glob
import pandas as pd
import typer


def get_vtk_files(vtk_directory: str) -> list[str]:
    """Get list of .vtk files

    Keyword arguments:
    vtk_directory -- path to directory with vtk files
    """
    files = sorted([file for file in glob.glob(f"{vtk_directory}/*.vtk")])
    return files


def get_timesteps(filename: str) -> list[str]:
    """Get timesteps from .sta file

    Keyword arguments
    filename -- path to .sta file
    """
    timesteps = []
    with open(filename) as f:
        lines = f.readlines()
        del lines[0]
        del lines[0]
        for line in lines:
            splited_line = line.split(" ")
            convergence = "".join(splited_line[-12:-10]).isnumeric()
            step = splited_line[-5:-4][0]
            if convergence:  # in some case time step entry can be duplicated
                timesteps.append(step)
    return timesteps


def find_array_id_by_name(point_data: vtk.vtkPointData, name: str) -> int | None:
    """Find array id by array name

    Keyword arguments:
    point_data -- vtk unstructured grid data
    name -- name of the array to find
    """
    for id in range(0, point_data.GetNumberOfArrays()):
        if point_data.GetArrayName(id) == name:
            return id
    return None


def main(vtk_directory: str, sta_file: str, output_file: str) -> None:
    """Main script function

    Keyword arguments:
    vtk_directory -- path to vtk directory
    sta_file -- path to CalculiX sta file
    output_file -- path to output csv file
    """
    max_K = []
    min_K = []
    max_C = []
    min_C = []
    max_F = []
    min_F = []
    files = get_vtk_files(vtk_directory)
    for filename in files:
        reader = vtk.vtkUnstructuredGridReader()
        reader.SetFileName(filename)
        reader.Update()
        point_data = reader.GetOutput().GetPointData()
        nt_id = find_array_id_by_name(point_data, "NT")
        nt = reader.GetOutput().GetPointData().GetArray(nt_id)

        array = numpy_support.vtk_to_numpy(nt)
        print(f"file: {filename}")
        print(f"max: {array.max()} K")
        print(f"min: {array.min()} K")
        max_K.append(array.max())
        max_C.append(array.max() - 273.15)
        min_K.append(array.min())
        min_C.append(array.min() - 273.15)
        max_F.append((array.max() - 273.15) * 1.8 + 32)
        min_F.append((array.min() - 273.15) * 1.8 + 32)

    timesteps = get_timesteps(sta_file)

    df = pd.DataFrame(
        data={
            "time [s]": timesteps,
            "max [K]": max_K,
            "max [C]": max_C,
            "max [F]": max_F,
            "min [K]": min_K,
            "min [C]": min_C,
            "min [F]": min_F,
        }
    )

    print()
    print(f"Collected {len(df)} rows")
    print(f"Dataframe memory usage {df.memory_usage(index=True).sum()}")
    df.to_csv(output_file)


if __name__ == "__main__":
    typer.run(main)
