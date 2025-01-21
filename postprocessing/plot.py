import matplotlib.pyplot as plt
import pandas as pd

file = "4WK_8W_1560s.csv"  # file path
time_max = 1560  # Simulation time
shift_kelwin = True  # shift kelvins to celsius

plt.style.use("./antmicro.mplstyle")

df = pd.read_csv(file)
time = df["Time"]
time = [((t + 1) / len(time)) * time_max for t in time]

if shift_kelwin:
    temperature = [T - 273.15 for T in df["max(Maximum)"]]

plt.plot(time, temperature, color="orange")
plt.grid()
plt.title("Temperature vs Time")
plt.xlabel("Time [s]")
plt.ylabel("Temperature [°C]")
plt.show()
