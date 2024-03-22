import subprocess
import dataclasses
import json
import pandas as pd

from tqdm import tqdm
from dataclasses import dataclass
from threading import Thread
from multiprocessing.pool import ThreadPool
from pathlib import Path
from configs.pim_config import Configuration, Statistics

gem5 = Path("build/ARM/gem5.opt")
out_dir_base = Path("pim_out")
pim_simulation = Path("configs/pim_simulation.py")


@dataclass
class WorkItem:
    configuration: Configuration
    statistics: Statistics | None = None

def run_gem5_process(work_item: WorkItem):
    serialized_configuration = json.dumps(
        dataclasses.asdict(work_item.configuration)
    )

    out_dir = out_dir_base / work_item.configuration.name

    out = subprocess.run(
        [
            gem5,
            "-d" + out_dir.as_posix(),
            pim_simulation,
            serialized_configuration,
        ],
        capture_output=True,
    )

    output = out.stdout.splitlines()[-1]
    work_item.statistics = Statistics(**json.loads(output))

workload_base_directory = Path("kernels")
workload_sub_directory = Path("aarch64-unknown-none/release")

workloads = [
    "vadd",
    "vmul",
    "haxpy",
    "gemv",
    "gemv_layers",
]

systems = [
    "HBM",
    "PIM-HBM",
]

configurations: list[Configuration] = []

for frequency in ["3GHz", "100GHz"]:
# for frequency in ["100GHz"]:
    for level in ["X1", "X2", "X3", "X4"]:
    # for level in ["X3"]:
        for system in systems:
            for workload in workloads:                
                executable = workload

                if system == "HBM":
                    executable = f"classic_{workload}"                

                executable = (
                    workload_base_directory
                    / level
                    / workload_sub_directory
                    / executable
                )

                configurations.append(
                    Configuration(
                        f"{workload}_{level}_{system}_{frequency}",
                        workload,
                        executable.as_posix(),
                        level,
                        system,
                        frequency,
                    )
                )

work_items = [WorkItem(configuration) for configuration in configurations]

with ThreadPool() as pool:
    for _ in tqdm(pool.imap_unordered(run_gem5_process, work_items), total=len(work_items)):
        pass


results: list[dict] = []

for work_item in work_items:
    result = dataclasses.asdict(work_item.configuration) | dataclasses.asdict(work_item.statistics)
    results.append(result)

dataframe = pd.DataFrame(results)
dataframe.to_csv("pim_results.csv", index=False)
