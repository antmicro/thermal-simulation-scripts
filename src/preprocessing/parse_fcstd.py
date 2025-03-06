import sys
import os
import typer
import json
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


def get_temperature(doc) -> list[tuple[str, float]]:
    temperature = []
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintTemperature":
            if obj.CFlux:
                temperature.append(tuple(("power", obj.CFlux.Value / 1000000)))
            if obj.Temperature:
                pass
                # FreeCad does not export temp to inp when cflux selected but stores value anyway
                # temperature.append(tuple(('temperature',obj.Temperature.Value)))
    return temperature


def get_heat_flux(doc) -> list[tuple[str, float]]:
    flux = []
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if obj.FilmCoef:
                flux.append(tuple(("Film_Coeff", obj.FilmCoef)))
            if obj.Emissivity:
                flux.append(tuple(("Emissivity", obj.Emissivity)))
    return flux


def generate_inp(inp: str) -> None:
    fea = ccxtools.FemToolsCcx()
    fea.update_objects()
    fea.setup_working_dir(inp)
    fea.setup_ccx()
    message = fea.check_prerequisites()
    if not message:
        fea.purge_results()
        fea.write_inp_file()


def main(fcstd: str, inp: str, log: str) -> None:

    fcstd_path = Path(fcstd).resolve()
    inp_path = Path(inp).resolve()
    log_path = Path(log).resolve()
    doc = App.openDocument(fcstd_path.as_posix())
    generate_inp(inp_path.as_posix())

    flux = get_heat_flux(doc)
    temperature = get_temperature(doc)
    params = {"heat source": {}, "heat dissipation": {}}

    for entry in temperature:
        params["heat source"].update({entry[0]: entry[1]})
    for entry in flux:
        params["heat dissipation"].update({entry[0]: entry[1]})
    with open((log_path / "simulation.json").as_posix(), "w") as f:
        json.dump(params, f)


if __name__ == "__main__":
    typer.run(main)
