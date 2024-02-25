import subprocess
import csv
import copy
import dataclasses
import json

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
        # print(out.stderr)
        # print(out.stdout)
        output = out.stdout.splitlines()[-1]
        self.statistics = Statistics(**json.loads(output))


workload_directory = Path("kernels")

workloads = [
    "classic_vadd",
    "classic_vmul",
    "classic_haxpy",
    "classic_gemv",
    # "classic_gemv_layers",
    "vadd",
    "vmul",
    "haxpy",
    "gemv",
    # "gemv_layers",
]

configurations: list[Configuration] = []

for frequency in ["3GHz", "100GHz"]:
    for workload in workloads:
        configurations.append(
            Configuration(workload + "_" + frequency, (workload_directory / workload).as_posix(), frequency)
        )

threads: list[Gem5Thread] = []

for configuration in configurations:
    thread = Gem5Thread(configuration)
    thread.start()
    threads.append(thread)

for thread in threads:
    thread.join()
    print(thread.configuration, thread.statistics)
