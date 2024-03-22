import matplotlib.pyplot as plt
import seaborn as sns
import polars as pl

from pathlib import Path

out_directory = Path("torch_plots_out")

system_mapping = {
    "HBM": "hbm",
    "PIM-HBM": "pim"
}

gem_df = pl.read_csv("pim_results.csv")
gem_df = gem_df.with_columns(pl.col("system").replace(system_mapping))
gem_df = gem_df.with_columns(
    pl.concat_str(["system", "frequency"], separator="_").alias("system")
)
gem_df = gem_df.select(["workload", "level", "system", "ticks"])

vega_df = pl.read_csv("vega_results.csv")
vega_df = vega_df.rename({"runtime": "ticks"})
vega_df = vega_df.with_columns(pl.lit("vega").alias("system"))

tesla_df = pl.read_csv("tesla_results.csv")
tesla_df = tesla_df.rename({"runtime": "ticks"})
tesla_df = tesla_df.with_columns(pl.lit("tesla").alias("system"))

df = pl.concat([gem_df, vega_df, tesla_df], how="diagonal")

workload_sets = [["vadd", "vmul", "haxpy"], ["gemv", "dnn"]]

workload_mapping = {
    "gemv_layers": "dnn",
}

df = df.with_columns(pl.col("workload").replace(workload_mapping))

# for workload_set in workload_sets:
#     temp_df = df.filter(pl.col("workload").is_in(workload_set))

g = sns.catplot(
    data=df.to_pandas(),
    kind="bar",
    x="level",
    y="ticks",
    hue="system",
    col="workload",
    palette="dark",
    alpha=0.6,
    height=6,
)

for name, data in df.group_by("system"):
    data = data.pivot(index=["level"], columns=["workload"], values=["ticks"])
    data.write_csv(out_directory / f"{name}.csv")
    print(data)

plt.show()
