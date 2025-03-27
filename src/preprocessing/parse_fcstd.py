import sys
import os
import typer
import json
import subprocess
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
    power_source_counter=0
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintTemperature":
            if obj.CFlux:
                power_source_counter+=1
                temperature.append(tuple((f"Power {power_source_counter}", obj.CFlux.Value / 1000000)))
            if obj.Temperature:
                pass
                # FreeCad does not export temp to inp when cflux selected but stores value anyway
                # temperature.append(tuple(('temperature',obj.Temperature.Value)))
    return temperature


def get_heat_flux(doc) -> list[tuple[str, float]]:
    flux = []
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if obj.FilmCoef and obj.ConstraintType == "Convection":
                flux.append(tuple(("Film coeff", obj.FilmCoef)))
            if obj.Emissivity and obj.ConstraintType == "Radiation":
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
    # Parse fcstd
    fcstd_path = Path(fcstd).resolve()
    inp_path = Path(inp).resolve()
    log_path = Path(log).resolve()
    doc = App.openDocument(fcstd_path.as_posix())
    generate_inp(inp_path.as_posix())
    # Tools versions
    freecad_version = App.Version()
    freecad_version = f"{freecad_version[0]}.{freecad_version[1]}.{freecad_version[2]} @{freecad_version[7]}"
    ccx = subprocess.Popen(args=["ccx", "-v"], stdout=subprocess.PIPE)
    ccx_version = (
        ccx.communicate()[0]
        .decode("utf-8")
        .removeprefix("\nThis is Version ")
        .removesuffix("\n\n")
    )
    # Generate simulation.json
    flux = get_heat_flux(doc)
    temperature = get_temperature(doc)

    # Update simulation.json
    params: dict = {
        "Heat source": {},
        "Heat dissipation": {},
        "Tools": {},
        "Design": {},
    }
    params["Design"] = fcstd_path.stem
    params["Tools"].update({"FreeCad": freecad_version, "CalculiX": ccx_version})
    total_power = 0
    for entry in temperature:
        total_power+=entry[1]
        params["Heat source"].update({entry[0]: entry[1]})
    params["Heat source"].update({"Total power":total_power}) 
    for entry in flux:
        params["Heat dissipation"].update({entry[0]: entry[1]})
    with open((log_path / "simulation.json").as_posix(), "w") as f:
        json.dump(params, f, indent=4)


if __name__ == "__main__":
    typer.run(main)
