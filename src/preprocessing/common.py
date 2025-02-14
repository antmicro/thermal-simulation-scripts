def parse_nodal_variables(
    lines: list[str], verbose: bool = False
) -> tuple[list[str], int] | str:
    """Parse nodal variables from .inp file

    Keyword arguments:
    lines -- list of lines
    verbose -- enable verbose printing
    """
    if verbose:
        print("NODAL VARIABLES\n  ", end="")
    for line_id, line in enumerate(lines):
        if line[0] != "*":
            variables = line.split(",")
            for id, var in enumerate(variables):
                variables[id] = var.replace("\n", "")
                if verbose:
                    if id < len(variables) - 1:
                        print(var, end=",")
                    else:
                        print(var, end="")
            return variables, line_id
    return "NA"


def parse_element_variables(
    lines: list[str], verbose: bool = False
) -> tuple[list[str], int] | str:
    """Parse element variables from .inp file

    Keyword arguments:
    lines -- list of lines
    verbose -- enable verbose printing
    """
    if verbose:
        print("ELEMENT VARIABLES\n  ", end="")
    for line_id, line in enumerate(lines):
        if line[0] != "*":
            variables = line.split(",")
            for id, var in enumerate(variables):
                variables[id] = var.replace("\n", "")
                if verbose:
                    if id < len(variables) - 1:
                        print(var, end=",")
                    else:
                        print(var, end="")
            return variables, line_id
    return "NA"


def parse_time(line: str) -> dict:
    """Parse simulation timmings from line
    Keyword arguments:
    line -- line with simulation timings
    """
    params = line.replace("\n", "").split(",")
    initial_time_step = params[0]
    simulation_time = params[1]
    min_time_increment = params[2]
    max_time_increment = params[3]
    return {
        "initial timestep": initial_time_step,
        "simulation time": simulation_time,
        "max increment": max_time_increment,
        "min increment": min_time_increment,
    }
