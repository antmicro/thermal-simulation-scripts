import sys
import os
import typer
import json
import subprocess
import logging
from pathlib import Path
from preprocessing.calculate_coef import calculate_film_coefficient
from preprocessing.common import get_config
from contextlib import redirect_stdout
from typing import Dict

# FREECAD_PATH points to sqashrootfs (extracted freecad appimage)
try:
    freecad_path = Path(os.environ["FREECAD_PATH"])
    sys.path.insert(0, str(freecad_path / "usr/lib/python3.11/site-packages"))
    sys.path.append(str(freecad_path / "usr/lib"))
    import FreeCAD
    from femtools import ccxtools
except KeyError:
    print("FREECAD_PATH is not set. Export it before running the script.")

log = logging.getLogger(__name__)


def get_initial_temperature(doc: FreeCAD) -> float:
    """Returns initial temperature constraint value in Kelvin."""
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintInitialTemperature":
            return obj.initialTemperature.Value
    else:
        raise Exception("Initial temperature constraint not specified")


def get_heat_source(doc: FreeCAD) -> Dict:
    heat_source = {}
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintTemperature":
            if obj.CFlux:
                heat_source.update({obj.Label: obj.CFlux.Value / 1000000})
            if obj.Temperature:
                pass
                # FreeCad does not export obj.Temperature to .INP file when the CFLUX constraint is selected
                # but initial value is stored in .FCStd anyway. Support for Temperature constraint is not implemented for now
    total_heat = sum(heat_source.values())
    heat_source.update({"Total": total_heat})
    return heat_source


def get_heat_flux(doc: FreeCAD) -> Dict:
    flux = {}
    for obj in doc.Objects:
        if obj.TypeId == "Fem::ConstraintHeatflux":
            if obj.FilmCoef and obj.ConstraintType == "Convection":
                flux.update({obj.Label: {"Film Coef": obj.FilmCoef}})
            if obj.Emissivity and obj.ConstraintType == "Radiation":
                flux.update({obj.Label: {"Emissivity": obj.Emissivity}})
    return flux


def open_fcstd(fcstd: str) -> FreeCAD:
    fcstd_path = Path(fcstd).resolve()
    return FreeCAD.openDocument(fcstd_path.as_posix())


def save_fcstd(doc: FreeCAD, fcstd: str) -> None:
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
    """Save coef with given type and value to .FCStd."""
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


def calc_film_coefs(fcstd: str, config_path: str) -> None:
    """Calculate & set new film coefficients for the middle value of a given temperature range."""
    # Get config temp
    config = get_config(config_path)

    # Calculate coeffs for the middle value of temperature range
    temp_mid: float = (
        float(config["temperature"]["max"] + config["temperature"]["min"]) / 2
    )
    doc = open_fcstd(fcstd)
    # Conversion from Kelvin to Celsius
    temp_initial = get_initial_temperature(doc) - 273.15
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


def set_solver(doc: FreeCAD) -> Dict:
    """Sets solver parameters & checks timings correctness."""
    solver_configuration = {}
    for obj in doc.Objects:
        if obj.TypeId != "Fem::FemSolverObjectPython":
            continue
        obj.AnalysisType = "thermomech"
        obj.ThermoMechType = "pure heat transfer"
        obj.ThermoMechSteadyState = False
        min_required_steps = int(10000 * (obj.TimeEnd / obj.TimeMaximumStep))
        if min_required_steps > obj.IterationsMaximum:
            logging.info(f"Increased simulation increments to {min_required_steps}")
            obj.IterationsMaximum = min_required_steps

        solver_configuration.update({"ThermoMechType": obj.ThermoMechType})
        solver_configuration.update(
            {"ThermoMechSteadyState": str(obj.ThermoMechSteadyState)}
        )
        solver_configuration.update({"Time End": obj.TimeEnd})
        solver_configuration.update({"Time Initial Step": obj.TimeInitialStep})
        solver_configuration.update({"Time Minimum Step": obj.TimeMinimumStep})
        solver_configuration.update({"Time Maximum Step": obj.TimeMaximumStep})
        solver_configuration.update({"Iterations Maximum": obj.IterationsMaximum})
    if not solver_configuration:
        raise Exception("Solver object not Found. Add ccx solver in .FCStd")
    return solver_configuration


def get_material(doc: FreeCAD) -> Dict:
    """Get parameters of the material constraint from .FCStd."""
    material = {}
    for obj in doc.Objects:
        if obj.TypeId != "App::MaterialObjectPython":
            continue
        material.update({"Density": obj.Material["Density"]})
        material.update({"Conductivity:": obj.Material["ThermalConductivity"]})
        material.update({"Expansion:": obj.Material["ThermalExpansionCoefficient"]})
        material.update({"Name:": obj.Material["Name"]})
        material.update({"Specific Heat:": obj.Material["SpecificHeat"]})

    if not material:
        raise Exception("Material object not Found. Add material constraint in .FCStd")
    return material


def main(fcstd: str, inp: str, log: str) -> None:
    inp_path = Path(inp).resolve()
    log_path = Path(log).resolve()
    doc = open_fcstd(fcstd)
    # Get tools versions
    freecad_version = FreeCAD.Version()
    freecad_version = f"{freecad_version[0]}.{freecad_version[1]}.{freecad_version[2]} @{freecad_version[7]}"
    ccx = subprocess.Popen(args=["ccx", "-v"], stdout=subprocess.PIPE)
    ccx_version = (
        ccx.communicate()[0]
        .decode("utf-8")
        .removeprefix("\nThis is Version ")
        .removesuffix("\n\n")
    )
    # Generate simulation.json
    params: Dict = {}
    params["Solver Configuration"] = set_solver(doc)
    params["Design"] = Path(fcstd).resolve().stem
    params["Tools"] = {"FreeCad": freecad_version, "CalculiX": ccx_version}
    params["Heat Dissipation"] = get_heat_flux(doc)
    params["Heat Source"] = get_heat_source(doc)
    params["Material"] = get_material(doc)
    params["Initial Temperature"] = get_initial_temperature(doc)

    save_fcstd(doc, fcstd)
    # Generate inp from updated .FCStd
    generate_inp(inp_path.as_posix())

    # Save simulation.json
    with open((log_path / "simulation.json").as_posix(), "w") as f:
        json.dump(params, f, indent=4)


if __name__ == "__main__":
    typer.run(main)
