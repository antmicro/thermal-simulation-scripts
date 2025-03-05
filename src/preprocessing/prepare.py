from preprocessing.common import (
    parse_nodal_variables,
    parse_element_variables,
    parse_time,
)
import typer


def main(filename: str, nt_hfl_only: bool) -> None:
    """
    Set simulation parameters

    Keyword arguments:
    filename -- path to simulation inp file
    nt_hfl_only -- simulate only structural temperature and heat flux
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    min_required_steps = 0
    simulation_steps = 0
    simulation_step_line_id = 0
    for id, line in enumerate(lines):
        if line.startswith("*NODE FILE"):
            nodal_variables, nodal_line_id = parse_nodal_variables(lines[id:])
            if nt_hfl_only:
                print("Set NT only in nodal variables")
                lines[nodal_line_id + id] = "NT\n"
            else:
                print(f"Set following nodal variables {''.join(nodal_variables)}")
        if line.startswith("*EL FILE"):
            element_variables, element_line_id = parse_element_variables(lines[id:])
            if nt_hfl_only:
                print("Set HFL only in element variables")
                lines[element_line_id + id] = "HFL\n"
            else:
                print(f"Set following element variables {''.join(element_variables)}")
        if line.startswith("*COUPLED TEMPERATURE-DISPLACEMENT"):
            timings = parse_time(lines[id + 1])
            if float(timings["max increment"]) != 0:
                min_required_steps = int(
                    10000
                    * (
                        float(timings["simulation time"])
                        / float(timings["max increment"])
                    )
                )

        if line.startswith("*STEP, INC="):
            simulation_steps = int(line.replace("*STEP, INC=", ""))
            print(f"Maximum increments: {simulation_steps}")
            simulation_step_line_id = id

    if min_required_steps > simulation_steps:
        print("Simulation increments count too low")
        print(f"Increasing to {min_required_steps}")
        lines[simulation_step_line_id] = f"*STEP, INC={min_required_steps}\n"

    with open(filename, "w") as f:
        f.writelines(lines)


if __name__ == "__main__":
    typer.run(main)
