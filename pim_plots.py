import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

df = pd.read_csv("pim_results.csv")

workloads = df["workload"].unique()

sns.set_theme()

def calc_speedup(x):
    return x.iat[0] / x.iat[1]

for workload in df["workload"].unique():
    workload_filter = df["workload"] == workload

    filtered_df = df[workload_filter]
    preprocessed_df = filtered_df.groupby(["workload", "level", "frequency"], as_index=False).agg({"ticks": calc_speedup}).rename(columns={"ticks":"speedup"})

    # print(preprocessed_df)
    # preprocessed_df.to_csv("plot.csv", index=False)

    g = sns.catplot(
        data=preprocessed_df, kind="bar",
        x="level", y="speedup", hue="frequency",
        palette="dark", alpha=.6, height=6
    )

    g.despine(left=True)
    g.set_axis_labels("", "Speedup")
    g.set(title=workload)
    g.legend.set_title("")

plt.show()
