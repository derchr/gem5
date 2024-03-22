import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

from pathlib import Path

out_directory = Path("pim_plots_out")

df = pl.read_csv("pim_results.csv")

workload_sets = {
    "vector": ["vadd", "vmul", "haxpy"],
    "matrix": ["gemv", "dnn"],
}

workload_mapping = {
    "gemv_layers": "dnn",
}

system_mapping = {
    "HBM": "hbm",
    "PIM-HBM": "pim"
}

def calc_speedup(tick_list):
    return tick_list[0] / tick_list[1]


df = df.with_columns(pl.col("workload").replace(workload_mapping))
df = df.with_columns(pl.col("system").replace(system_mapping))

df = df.group_by(
    ["workload", "level", "frequency"], maintain_order=True
).agg(pl.col("ticks").map_elements(calc_speedup).alias("speedup"))

for name, data in df.group_by(
    "frequency",
    pl.when(pl.col("workload").is_in(workload_sets["vector"]))
    .then(pl.lit("vector"))
    .when(pl.col("workload").is_in(workload_sets["matrix"]))
    .then(pl.lit("matrix")),
):
    plot = sns.catplot(
        data=data.to_pandas(),
        kind="bar",
        x="level",
        y="speedup",
        hue="workload",
        palette="dark",
        alpha=0.6,
        height=6,
    )
    plot.set_axis_labels("Level", "Speedup")
    plot.set(title=name[0] + name[1])

    plot.fig.subplots_adjust(top=0.95)

    data = data.pivot(index=["level"], columns=["workload"], values=["speedup"])
    print(data)

    data.write_csv(out_directory / f"{name[1]}_{name[0]}.csv")

plt.show()
