import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import typer
import json
import os


def ensure_output_directory(output_dir: str) -> None:
    """Ensure that the output directory exists."""
    os.makedirs(output_dir, exist_ok=True)


def read_simulation_data(filename: str) -> pd.DataFrame:
    """Read simulation results from .csv file
    Keyword arguments:
    filename -- name of simulation result csv file
    """
    df = pd.read_csv(filename)
    return df


def plot(
    temperature: pd.Series | pd.DataFrame,
    time: pd.Series | pd.DataFrame | np.ndarray,
    title: str,
    unit: str,
    output_dir: str,
) -> None:
    """Generate temperature plot
    Keyword arguments:
    temperature -- temperature series
    time -- time series
    title -- chart title
    unit -- unit of temperature
    output_dir -- path to chart directory
    """
    ensure_output_directory(output_dir)
    plt.style.use(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "antmicro.mplstyle")
    )
    plt.plot(time, temperature, color="orange")
    plt.grid()
    plt.title(f"Temperature vs {title}")
    plt.ylabel(f"Temperature [{unit}]")
    plt.xlabel("Time [s]")
    plt.savefig(f"{output_dir}/temperature_vs_time_{title}_{unit}.jpg")
    plt.close()


def plot_iterations(counts: np.ndarray, bins: np.ndarray, output_dir: str) -> None:
    """Plot iteration over time graph
    Keyword arguments:
    counts -- number of counts in bins
    bins -- number of bins
    output_dir -- path to graph storage dir
    """
    plt.style.use(
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "antmicro.mplstyle")
    )
    plt.stairs(counts, bins, color="orange")
    plt.grid()
    plt.title("Itterations over time")
    plt.xlabel("Time [s]")
    plt.ylabel("Itterations")
    plt.savefig(f"{output_dir}/itteration_vs_time.jpg")
    plt.close()


def get_time_steps(simulation_json: str) -> float:
    """Get number of simulation time steps from simulation json settings
    Keyword arguments:
    simulation_json -- path to simulation json file
    """
    with open(simulation_json, "r") as file:
        data = json.load(file)
    return float(data["Timings"]["Simulation time"]) / float(
        data["Timings"]["Max increment"]
    )


def main(
    data_file: str, output_dir: str = "graphs", simulation_json: str | None = None
) -> None:
    """Main script method
    Keyword arguments:
    data_file -- path to simulation output file csv
    output_dir -- path to output directory
    simulation_json -- (optional) path to json file
    """
    if not output_dir:
        output_dir = "graphs"
    ensure_output_directory(output_dir)
    sim_data = read_simulation_data(data_file)

    max_C = sim_data["max [C]"]
    max_K = sim_data["max [K]"]
    min_C = sim_data["min [C]"]
    min_K = sim_data["min [K]"]
    time = sim_data["time [s]"]

    # Plot max and min values over time
    plot(max_C, time, "Time (maximum)", "C", output_dir)
    plot(max_K, time, "Time (maximum)", "K", output_dir)
    plot(min_C, time, "Time (minimum)", "C", output_dir)
    plot(min_K, time, "Time (minimum)", "K", output_dir)

    # Compute and plot differences
    diff_C = max_C - min_C
    diff_K = max_K - min_K
    plot(diff_C, time, "Time (difference)", "C", output_dir)
    plot(diff_K, time, "Time (difference)", "K", output_dir)

    # Plot values over simulation steps
    simulation_steps = np.arange(0, len(max_K))

    plot(max_K, simulation_steps, "Simulation steps (maximum)", "K", output_dir)
    plot(max_C, simulation_steps, "Simulation steps (maximum)", "C", output_dir)

    plot(min_K, simulation_steps, "Simulation steps (minimum)", "K", output_dir)
    plot(min_C, simulation_steps, "Simulation steps (minimum)", "C", output_dir)

    plot(diff_K, simulation_steps, "Simulation steps (difference)", "K", output_dir)
    plot(diff_C, simulation_steps, "Simulation steps (difference)", "C", output_dir)

    if simulation_json is not None:
        counts, bins = np.histogram(time, bins=int(get_time_steps(simulation_json)))
        plot_iterations(counts, bins, output_dir)


if __name__ == "__main__":
    typer.run(main)
