import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv("pim_results.csv")

frequency_filter = df["frequency"] == "3GHz"

workloads = df["workload"].unique()

fig, ax = plt.subplots()

width = 0.25
index = 0

# for workload in workloads:
for level in df["level"].unique():
    level_filter = df["level"] == level

    for pim in [False, True]:
        workload_filter = df["workload"] == "vadd"

        filtered_df = df[level_filter & workload_filter & frequency_filter]
        print(filtered_df)

        x = np.arange(len(filtered_df))

        offset = 6*width * index
        print(x+offset)
        bars = ax.bar(x + offset, "ticks", width, data=filtered_df, label=level)
        # ax.bar_label(bars, padding=2)
        index += 1

ax.legend(loc="upper left")
plt.show()
