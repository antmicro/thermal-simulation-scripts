import matplotlib.pyplot as plt
import pandas as pd
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    prog='plot_meas',
    description='Plot measurments vs simulation  temperature(time) graph')
parser.add_argument('-t', '--time', action='store',type=int,required=True, help='Define max time [s]')
parser.add_argument('-s', '--sim', action='store',type=str,required=True, help='Path to simulation csv')
parser.add_argument('-m', '--meas', action='store',type=str,required=True, help='Path to measurments csv')
parser.add_argument('-k', '--kelvin', action='store_true',required=False, help='Use Kelvin degrees')
parser.add_argument('-n', '--name', action='store',default='Simulation vs measurments', help ='Graph name')

args=parser.parse_args()
sim_file = Path(args.sim).resolve()
meas_file = Path(args.meas).resolve()
time_max = args.time  
print(meas_file)

plt.style.use("./antmicro.mplstyle")

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

plt.plot(time_sim, temperature_sim, "--", color="white", label="Simulation")
plt.plot(time_meas, temperature_meas, color="orange", label="Measurements")
# Axis range
#plt.ylim(25,60)
plt.xlim(-30,time_max)
plt.title(args.name)
plt.xlabel("Time [s]")
plt.legend()
if args.kelvin:
    plt.ylabel("Temperature [K]")
else:
    plt.ylabel("Temperature [°C]")
plt.grid()
plt.show()
