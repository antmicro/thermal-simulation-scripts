#!/bin/python
import json
import typer

from preprocessing.common import (
    parse_nodal_variables,
    parse_element_variables,
    parse_time,
)


class ParsingException(Exception):
    pass


def parse_initial_temperature(lines: list[str]) -> str:
    """
    Get initial temperature from simulation settings file

    Keyword arguments:
    lines -- list of lines from .inp file
    """
    for line in lines:
        if not line.startswith("*"):
            return line.split(",")[-1:][0].replace("\n", "")
    raise ParsingException("Initial temperature not found in the input file.")


def parse_material(lines: list[str]) -> dict:
    """
    Parse material settings from simulation file

    Keyword arguments:
    lines -- list of lines from .inp file
    """
    name = lines[0].replace("*MATERIAL,NAME= ", "").replace("\n", "")
    elastic = lines[3].replace("\n", "")
    density = lines[5].replace("\n", "")
    conductivity = lines[7].replace("\n", "")
    expansion = lines[9].replace("\n", "")
    specific_heat = lines[11].replace("\n", "")
    return {
        "name": name,
        "elastic": elastic,
        "density": density,
        "conductivity": conductivity,
        "expansion": expansion,
        "specific heat": specific_heat,
    }


def print_materials(materials: list[dict]) -> None:
    """
    Print material parameters

    Keyword arguments:
    materials -- list of materials settings
    """
    print("MATERIALS")
    for material in materials:
        print(f"  Name: {material['name']}")
        print(f"    Conductivity  {material['conductivity']}")
        print(f"    Specific heat {material['specific heat']}")
        print(f"    Expansion     {material['expansion']}")
        print(f"    Density       {material['density']}")
        print(f"    Elastic       {material['elastic']}")


def save_json(content: dict, filename: str) -> None:
    """
    Save simulation settings file

    Keyword arguments:
    content -- file content to save
    filename -- path to file
    """
    with open(filename, "r+") as f:
        data = json.load(f)
        data.update(content)
        f.seek(0)
        json.dump(data, f)


def main(filename: str, output_file: str) -> None:
    """
    Get simulation settings from ccx .inp file

    Keyword arguments:
    filename -- path to CalculiX .inp file
    output_file -- path to output file
    """
    simulation_settings = {
        "simulation type": "",
        "timings": dict,
        "materials": list,
        "initial temperature": float,
        "nodal variables": list,
        "element variables": list,
        "max iterations": int,
    }

    with open(filename) as f:
        lines = f.readlines()

    materials = []
    for id, line in enumerate(lines):
        if (
            line.startswith("*COUPLED TEMPERATURE-DISPLACEMENT")
            or line.startswith("*UNCOUPLED TEMPERATURE-DISPLACEMENT")
            or line.startswith("*HEAT TRANSFER")
        ):
            sim_type = line.replace("*", "").replace("\n", "")
            simulation_settings["simulation type"] = sim_type
            print("SIMULATION TYPE")
            print(f"  {sim_type}")
            timings = parse_time(lines[id + 1])
            simulation_settings["timings"] = timings
            print("SIMULATION TIMINGS")
            print(f'  Simulation Time:  {timings["simulation time"]} s')
            print(f'  Max increment:    {timings["max increment"]} s')
            print(f'  Min increment:    {timings["min increment"]} s')
            print(f'  Initial timestep: {timings["initial timestep"]} s')

        if line.startswith("*MATERIAL"):
            material = parse_material(lines[id - 1 :])
            materials.append(material)
        if line.startswith("*INITIAL CONDITIONS,TYPE=TEMPERATURE"):
            simulation_settings["initial temperature"] = parse_initial_temperature(
                lines[id:]
            )
            print("GLOBAL CONSTRAINTS")
            print(
                f'  Initial temperature: {simulation_settings["initial temperature"]} K'
            )
        if line.startswith("*NODE FILE"):
            nodal_variables, _ = parse_nodal_variables(lines[id:], verbose=True)
            simulation_settings["nodal variables"] = nodal_variables
        if line.startswith("*EL FILE"):
            element_variables, _ = parse_element_variables(lines[id:], verbose=True)
            simulation_settings["element variables"] = element_variables
        if line.startswith("*STEP, INC="):
            iterations = int(line.replace("*STEP, INC=", ""))
            print(f"Maximum iterations: {iterations}")
            simulation_settings["max iterations"] = iterations

    print_materials(materials)
    simulation_settings["materials"] = materials
    save_json(simulation_settings, output_file)


if __name__ == "__main__":
    typer.run(main)
