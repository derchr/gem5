import matplotlib.pyplot as plt
import seaborn as sns
import polars as pl
import numpy as np

from pathlib import Path

workload_order = {val: idx for idx, val in enumerate(["vadd", "vmul", "haxpy", "gemv", "gemv_layers"])}

workload_mapping = {
    "vadd": "VADD",
    "vmul": "VMUL",
    "haxpy": "HAXPY",
    "gemv": "GEMV",
    "gemv_layers": "DNN",
}

out_directory = Path("tables_out")

df = pl.read_csv("pim_results.csv")
df = df.select(["workload", "level", "system", "frequency", "ticks"])

for name, data in df.group_by(["frequency"], maintain_order=True):
    data = data.pivot(index=["workload", "level"], columns=["system"], values=["ticks"])
    data = data.sort(pl.col("workload").replace(workload_order))
    data = data.with_columns(pl.col("workload").replace(workload_mapping))
    data = data.rename({"HBM": "hbm", "PIM-HBM": "pim"})
    print(data)

    data.write_csv(out_directory / f"simulations_{name[0]}.csv")

vega_df = pl.read_csv("vega_results.csv")
vega_df = vega_df.with_columns(system=pl.lit("vega"))

tesla_df = pl.read_csv("tesla_results.csv")
tesla_df = tesla_df.with_columns(system=pl.lit("tesla"))

torch_df = pl.concat([vega_df, tesla_df])

torch_df = torch_df.pivot(index=["workload", "level"], columns=["system"], values=["runtime"])
torch_df = torch_df.sort(pl.col("workload").replace(workload_order))
torch_df = torch_df.with_columns(pl.col("workload").replace(workload_mapping))
print(torch_df)

torch_df.write_csv(out_directory / "torch.csv")
