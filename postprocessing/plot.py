import matplotlib.pyplot as plt
import pandas as pd

file = ""  # file path to simulation csv file
time_max =   # Simulation time in seconds
shift_kelwin = True  # shift kelvins to celsius

plt.style.use("./antmicro.mplstyle")

df = pd.read_csv(file)
time = df["Time"]
time = [((t + 1) / len(time)) * time_max for t in time]

if shift_kelwin:
    temperature = [T - 273.15 for T in df["max(Maximum)"]]
else:
    temperature = [T for T in df["max(Maximum)"]]

plt.plot(time, temperature, color="orange")
plt.grid()
plt.title("Temperature vs Time")
plt.xlabel("Time [s]")

if shift_kelwin:
    plt.ylabel("Temperature [°C]")
else:
    plt.ylabel("Temperature [K]")
plt.show()
