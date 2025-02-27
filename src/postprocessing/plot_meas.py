import matplotlib.pyplot as plt
import pandas as pd
import argparse
import sys
import os
from pathlib import Path

parser = argparse.ArgumentParser(
    prog="plot_meas",
    description="Plot measurments vs simulation  temperature(time) graph",
)
parser.add_argument(
    "-t", "--time", action="store", type=int, required=True, help="Define max time [s]"
)
parser.add_argument(
    "-s",
    "--sim",
    action="store",
    type=str,
    required=True,
    help="Path to simulation csv",
)
parser.add_argument(
    "-m",
    "--meas",
    action="store",
    type=str,
    required=True,
    help="Path to measurments csv",
)
parser.add_argument(
    "-k", "--kelvin", action="store_true", required=False, help="Use Kelvin degrees"
)
parser.add_argument(
    "-n",
    "--name",
    action="store",
    default="Simulation vs measurments",
    help="Graph name",
)
parser.add_argument(
    "-l",
    "--legend",
    action="store",
    choices=["upper left", "upper right", "center", "lower left", "lower right"],
    type=str,
    default="best",
    help="Set legend location",
)

def main():
    args = parser.parse_args(sys.argv[1:])
    sim_file = Path(args.sim).resolve()
    meas_file = Path(args.meas).resolve()
    sim = pd.read_csv(sim_file)
    meas = pd.read_csv(meas_file)
    time_sim = sim["time [s]"]
    time_meas = meas["time [s]"]

    if args.kelvin:
        temperature_sim = [T for T in sim["max [K]"]]
        temperature_meas = [T for T in meas["temp [K]"]]

    else:
        temperature_sim = [T for T in sim["max [C]"]]
        temperature_meas = [T for T in meas["temp [C]"]]
    
    plt.style.use(os.path.join(os.path.abspath(os.path.dirname(__file__)), "antmicro.mplstyle"))
    plt.plot(time_sim, temperature_sim, "--", color="white", label="Simulation")
    plt.plot(time_meas, temperature_meas, color="orange", label="Measurements")
    plt.legend(loc=args.legend)
    # Axis range
    # plt.ylim(25,70)
    plt.xlim(-30, args.time)
    plt.title(args.name)
    plt.xlabel("Time [s]")
    if args.kelvin:
        plt.ylabel("Temperature [K]")
    else:
        plt.ylabel("Temperature [°C]")
    plt.grid()
    plt.show()
