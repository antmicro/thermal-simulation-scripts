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
    from femtools import ccxtools
except KeyError:
    print("FREECAD_PATH is not set. Export it before running the script.")

def main(fcstd_in:str,fcstd_out:str, coeff_type:str, coeff_value:float)->None:
    doc = App.openDocument(Path(fcstd_in).resolve().as_posix())
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if coeff_type == "film":
                obj.FilmCoef = coeff_value
                obj.Emissivity = 0
            if coeff_type == "emissivity":
                obj.Emissivity = coeff_value
                obj.FilmCoef = 0
    if fcstd_out:
        doc.saveAs(Path(fcstd_out).resolve().as_posix())
    else:
        doc.save()
    
if __name__ == "__main__":
    typer.run(main)
