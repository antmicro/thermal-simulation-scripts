import matplotlib.pyplot as plt
import pandas as pd

sim_file = ""  # file path to simulation csv file
meas_file = ""
time_max = 6000  # simulation time in seconds
shift_kelwin = False  # shift kelvins to celsius


plt.style.use("./antmicro.mplstyle")

sim = pd.read_csv(sim_file)
meas = pd.read_csv(meas_file)
time_sim = sim["time [s]"]
time_meas = meas["time [s]"]

if shift_kelwin:
    temperature_sim = [T - 273.15 for T in sim["max [K]"]]
    temperature_meas = [T - 273.15 for T in meas["temp"]]

else:
    temperature_sim = [T for T in sim["max [C]"]]
    temperature_meas = [T for T in meas["temp"]]

plt.plot(time_sim, temperature_sim, "--", color="white", label="Simulation")
plt.plot(time_meas, temperature_meas, color="orange", label="Measurements")
# Set Y axis range
plt.ylim(25,60)
plt.xlim(-10,6000)
# plt.yscale('log')
plt.title("RPI5 enclosure temperature vs time (2.5W)")
plt.xlabel("Time [s]")
plt.legend()
plt.ylabel("Temperature [°C]")
plt.grid()
plt.show()
