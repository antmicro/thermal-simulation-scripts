import matplotlib.pyplot as plt
import pandas as pd

file = "4WK_12_5W_1560s_Meas.csv"  # file path
time_max = 1560  # Simulation time
shift_kelwin = True  # shift kelvins to celsius

plt.style.use("./antmicro.mplstyle")

df = pd.read_csv(file)
time = df["Time"]
time = [((t + 1) / len(time)) * time_max for t in time]

if shift_kelwin:
    temperature_sim = [T - 273.15 for T in df["max(Maximum)"]]
    temperature_meas = [T - 273.15 for T in df["meas"]]
plt.plot(time, temperature_sim, "--", color="white", label="Simulation")
plt.plot(time, temperature_meas, color="orange", label="Measurements")

plt.title("Temperature vs Time (12.5W)")
plt.xlabel("Time [s]")
plt.legend()
plt.ylabel("Temperature [°C]")
plt.grid()
plt.show()

plt.imsave("Measurement_vs_simulation.png")
