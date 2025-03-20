import sys
import os
import typer
from pathlib import Path

# FREECAD_PATH points to sqashrootfs (extracted freecad appimage)
try:
    freecad_path = Path(os.environ["FREECAD_PATH"])
    sys.path.insert(0, str(freecad_path / "usr/lib/python3.11/site-packages"))
    sys.path.append(str(freecad_path / "usr/lib"))
    import FreeCAD as App
except KeyError:
    print("FREECAD_PATH is not set. Export it before running the script.")

def main(fcstd:str, coef_type:str, coef_value:float)->None:
    fcstd_file = Path(fcstd).resolve().as_posix()
    doc = App.openDocument(fcstd_file)
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if coef_type == "film":
                obj.ConstraintType = "Convection"
                obj.FilmCoef = coef_value
            if coef_type == "emissivity":
                obj.ConstraintType = "Radiation"
                obj.Emissivity = coef_value

    doc.save()
    # FreeCad creates redundant .FCStd1 file
    new_path = Path(fcstd).resolve().as_posix()+'1'
    os.remove(new_path)

if __name__ == "__main__":
    typer.run(main)
