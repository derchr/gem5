import subprocess
import csv
import copy
import dataclasses
import json
import pandas as pd

from threading import Thread
from pathlib import Path
from typing import Dict
from configs.pim_config import Configuration, Statistics

gem5 = Path("build/ARM/gem5.opt")
out_dir_base = Path("pim_out")
pim_simulation = Path("configs/pim_simulation.py")


class Gem5Thread(Thread):
    def __init__(self, configuration: Configuration) -> None:
        super().__init__()
        self.configuration = configuration

    def run(self):
        serialized_configuration = json.dumps(
            dataclasses.asdict(self.configuration)
        )

        out_dir = out_dir_base / configuration.name

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
        self.statistics = Statistics(**json.loads(output))


workload_base_directory = Path("kernels")
workload_sub_directory = Path("aarch64-unknown-none/release")

workloads = [
    "vadd",
    "vmul",
    "haxpy",
    "gemv",
    # "gemv_layers",
]

systems = [
    "HBM",
    "PIM-HBM",
]

configurations: list[Configuration] = []

for frequency in ["3GHz", "100GHz"]:
    for level in ["X1", "X2", "X3", "X4"]:        
        for system in systems:
            for workload in workloads:
                if workload == "gemv_layers" and level != "X4":
                    continue
                
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
                        f"{workload}_{level}_{frequency}",
                        workload,
                        executable.as_posix(),
                        level,
                        system == "PIM-HBM",
                        frequency,
                    )
                )

threads: list[Gem5Thread] = []

for configuration in configurations:
    thread = Gem5Thread(configuration)
    thread.start()
    threads.append(thread)

results: list[dict] = []

for thread in threads:
    thread.join()

    result = dataclasses.asdict(thread.configuration) | dataclasses.asdict(thread.statistics)
    results.append(result)

dataframe = pd.DataFrame(results)
dataframe.to_csv("pim_results.csv", index=False)
