import sys
import os
import typer
import json
import subprocess
import logging
from pathlib import Path
from preprocessing.calculate_coef import calculate_film_coefficient
from contextlib import redirect_stdout

# FREECAD_PATH points to sqashrootfs (extracted freecad appimage)
try:
    freecad_path = Path(os.environ["FREECAD_PATH"])
    sys.path.insert(0, str(freecad_path / "usr/lib/python3.11/site-packages"))
    sys.path.append(str(freecad_path / "usr/lib"))
    import FreeCAD as App
    from femtools import ccxtools
except KeyError:
    print("FREECAD_PATH is not set. Export it before running the script.")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_initial_temperature(doc: App) -> float:
    """Returns initial temperature constraint value in Celcius degrees"""
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintInitialTemperature":
            return obj.initialTemperature.Value - 273.15
    else:
        raise Exception("Initial temperature constraint not specified")


def get_temperature(doc: App) -> list[tuple[str, float]]:
    temperature = []
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintTemperature":
            if obj.CFlux:
                temperature.append(tuple((obj.Label, obj.CFlux.Value / 1000000)))
            if obj.Temperature:
                pass
                # FreeCad does not export temp to .inp when cflux selected but stores value anyway
                # Can be handled by changing temperature constraint type, not implementing for now
                # temperature.append(tuple(('temperature',obj.Temperature.Value)))
    return temperature


def get_heat_flux(doc: App) -> list[tuple]:
    flux = []
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if obj.FilmCoef and obj.ConstraintType == "Convection":
                flux.append((obj.Label, "Film coeff", obj.FilmCoef))
            if obj.Emissivity and obj.ConstraintType == "Radiation":
                flux.append((obj.Label, "Emissivity", obj.Emissivity))
    return flux


def open_fcstd(fcstd: str) -> App:
    fcstd_path = Path(fcstd).resolve()
    return App.openDocument(fcstd_path.as_posix())


def save_fcstd(doc: App, fcstd: str):
    doc.save()
    # FreeCad creates redundant files - remove them
    new_path = Path(fcstd).parents[0]
    files = os.listdir(new_path.resolve().as_posix())
    for file in files:
        if file.endswith(".FCStd1") or file.endswith(".FCBak"):
            os.remove(new_path / Path(file))


def generate_inp(inp: str) -> None:
    fea = ccxtools.FemToolsCcx()
    fea.update_objects()
    logging.info(f"Setting up working directory: {inp}")
    fea.setup_working_dir(inp)
    logging.info("Setting up CCX solver...")
    fea.setup_ccx()
    logging.info("Checking prerequisites...")
    message = fea.check_prerequisites()
    if not message:
        fea.purge_results()
        logging.info("Writing .inp file...")
        # Remove stdout
        with open(os.devnull, "w") as devnull:
            with redirect_stdout(devnull):
                fea.write_inp_file()
        logging.info("Successfully generated the .inp file.")
    else:
        logging.error(f"Prerequisite check failed: {message}")


def set_coef(fcstd: str, coef_type: str, coef_value: float, coef_name: str) -> None:
    doc = open_fcstd(fcstd)
    # Check if requested name exists in constraints
    if coef_name:
        match_count = 0
        for obj in doc.Objects:
            if obj.TypeId != "Fem::ConstraintHeatflux":
                continue
            if obj.Label == coef_name:
                match_count += 1
        if match_count == 0:
            raise Exception(f"{coef_name} label not in heat flux objects")
    # Set coefficients
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if coef_name and obj.Label != coef_name:
                continue
            if coef_type == "film":
                obj.ConstraintType = "Convection"
                obj.FilmCoef = coef_value
            if coef_type == "emissivity":
                obj.ConstraintType = "Radiation"
                obj.Emissivity = coef_value
    save_fcstd(doc, fcstd)


def get_coef(fcstd: str, config_path: str):
    # Get config temp
    with open(Path(config_path).resolve().as_posix(), "r") as file:
        config: dict = json.load(file)

    # Calculate coeffs for the middle value of temperature range
    temp_mid: float = (
        float(config["temperature"]["max"] + config["temperature"]["min"]) / 2
    )
    doc = open_fcstd(fcstd)
    temp_initial = get_initial_temperature(doc)
    logging.info("Calculating film coefficients...")
    for coef_name in config["film"]:
        film = calculate_film_coefficient(
            temp_initial,
            temp_mid,
            config["film"][coef_name][1],
            config["film"][coef_name][0],
        )
        set_coef(fcstd, "film", film, coef_name)
        logging.info(f"{coef_name} = {film}")


def main(fcstd: str, inp: str, log: str) -> None:
    inp_path = Path(inp).resolve()
    log_path = Path(log).resolve()
    doc = open_fcstd(fcstd)
    generate_inp(inp_path.as_posix())
    # Get tools versions
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
    params["Design"] = Path(fcstd).resolve().stem
    params["Tools"].update({"FreeCad": freecad_version, "CalculiX": ccx_version})
    total_power: float = 0
    for entry in temperature:
        total_power += entry[1]
        params["Heat source"].update({entry[0]: entry[1]})
    params["Heat source"].update({"Total power": total_power})
    for entry in flux:
        if len(entry) == 3:
            params["Heat dissipation"].update({entry[0]: [entry[1], entry[2]]})
    # Save simulation.json
    with open((log_path / "simulation.json").as_posix(), "w") as f:
        json.dump(params, f, indent=4)


if __name__ == "__main__":
    typer.run(main)
