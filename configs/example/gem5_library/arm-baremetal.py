from gem5.isas import ISA
from m5.objects import (
    ArmDefaultRelease,
)
from gem5.utils.requires import requires
from gem5.resources.workload import CustomWorkload
from gem5.resources.resource import BinaryResource
from gem5.simulate.simulator import Simulator
from m5.objects import VExpress_GEM5_Foundation
from gem5.components.boards.arm_baremetal_board import ArmBareMetalBoard
from gem5.components.memory import DRAMSysDDR3_1600
from gem5.components.processors.cpu_types import CPUTypes
from gem5.components.processors.simple_processor import SimpleProcessor

requires(isa_required=ISA.ARM)

from gem5.components.cachehierarchies.classic.private_l1_private_l2_cache_hierarchy import (
    PrivateL1PrivateL2CacheHierarchy,
)
from gem5.components.cachehierarchies.classic.no_cache import NoCache

cache_hierarchy = PrivateL1PrivateL2CacheHierarchy(
    l1d_size="16kB", l1i_size="16kB", l2_size="256kB"
)
# cache_hierarchy = NoCache()

memory = DRAMSysDDR3_1600(recordable=True)
processor = SimpleProcessor(cpu_type=CPUTypes.O3, num_cores=1, isa=ISA.ARM)
release = ArmDefaultRelease()
platform = VExpress_GEM5_Foundation()

board = ArmBareMetalBoard(
    clk_freq="3GHz",
    processor=processor,
    memory=memory,
    cache_hierarchy=cache_hierarchy,
    release=release,
    platform=platform,
)

board.m5ops_base = 0x10010000

workload = CustomWorkload(
    "set_baremetal_workload",
    {
        "kernel": BinaryResource("aarch64"),
    },
)
board.set_workload(workload)

simulator = Simulator(board=board)
simulator.run()
