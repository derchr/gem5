import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from pathlib import Path

df = pd.read_csv("pim_results.csv")

sns.set_theme()

def calc_speedup(x):
    return x.iat[0] / x.iat[1]

workload_sets = [["vadd", "vmul", "haxpy"], ["gemv", "gemv_layers"]]

for workload_set in workload_sets:
    workload_filter = df["workload"].isin(workload_set)

    for frequency in df["frequency"].unique():
        frequency_filter = df["frequency"] == frequency

        filtered_df = df[workload_filter & frequency_filter]
        print(filtered_df)
        preprocessed_df = filtered_df.groupby(["workload", "level", "frequency"], as_index=False).agg({"ticks": calc_speedup}).rename(columns={"ticks":"speedup"})

        print(preprocessed_df)
        # preprocessed_df.to_csv("plot.csv", index=False)

        g = sns.catplot(
            data=preprocessed_df, kind="bar",
            x="level", y="speedup", hue="workload",
            palette="dark", alpha=.6, height=6
        )

        g.despine(left=True)
        g.set_axis_labels("", "Speedup")
        g.set(title=frequency)
        g.legend.set_title("")

        for workload in workload_set:
            export_df = preprocessed_df[preprocessed_df["workload"] == workload]

            filename = f"{workload}_{frequency}.csv"
            directory = Path("plots_out")
            export_df.to_csv(directory / filename, index=False)

plt.show()
