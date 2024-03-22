import re
import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import timedelta

from pathlib import Path

stats_dir = Path("pim_out")

runtime_dict: dict[str, list[any]] = {}

for element in stats_dir.iterdir():
    print(element.name)
    matches = re.search(r'(\w+)_(\w+)_(\w*-*\w*)_(\w+)', element.name)
    workload, level, system, freq = matches.group(1), matches.group(2), matches.group(3), matches.group(4)

    with open(element / "stats.txt") as f:
        regex = re.compile(r'hostSeconds\ +(\d+.\d+).*')
        for line in f:
            result = regex.search(line)
            if result is not None:
                # implicitly only get last match in file...
                runtime = result.group(1)

    runtime_dict.setdefault("workload", []).append(workload)
    runtime_dict.setdefault("level", []).append(level)
    runtime_dict.setdefault("system", []).append(system)
    runtime_dict.setdefault("freq", []).append(freq)
    runtime_dict.setdefault("runtime", []).append(float(runtime))

df = pl.DataFrame(runtime_dict)
df = df.filter((pl.col("freq") == "100GHz") & (pl.col("level") == "X3"))
df = df.drop("freq")
print(df)

plot = sns.catplot(
    data=df.to_pandas(),
    kind="bar",
    x="system",
    y="runtime",
    hue="workload",
    palette="dark",
    alpha=0.6,
    height=6,
)
plot.set_axis_labels("PIM vs. Non-PIM", "Runtime [s]")
plot.set(title="Wallclock Time")

plot.fig.subplots_adjust(top=0.95)

plt.show()
