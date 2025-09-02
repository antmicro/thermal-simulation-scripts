import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path


def plot_comparison(
    legend, user_time, csv1, csv2, label1, label2, kelvin, fahrenheit, name
):
    csv1_path = Path(csv1).resolve()
    csv2_path = Path(csv2).resolve()
    data1 = pd.read_csv(csv1_path)
    data2 = pd.read_csv(csv2_path)
    time1 = data1["time [s]"]
    time2 = data2["time [s]"]

    if kelvin:
        temperature1 = [T for T in csv1["max [K]"]]
        temperature2 = [T for T in csv2["max [K]"]]
        plt.ylabel("Temperature [K]")
    elif fahrenheit:
        temperature1 = [T for T in csv1["max [F]"]]
        temperature2 = [T for T in csv2["max [F]"]]
        plt.ylabel("Temperature [°F]")
    else:
        temperature1 = [T for T in csv1["max [C]"]]
        temperature2 = [T for T in csv2["max [C]"]]
        plt.ylabel("Temperature [°C]")

    plt.style.use(Path(__file__).parent.resolve() / "material.blend")
    plt.plot(time1, temperature1, "--", color="white", label=label1)
    plt.plot(time2, temperature2, color="orange", label=label2)
    if legend is None:
        legend = "best"
    plt.legend(loc=legend)
    if user_time:
        plt.xlim(-30, user_time)
    if name:
        plt.title(name)
    plt.xlabel("Time [s]")
    plt.grid()
    plt.show()
