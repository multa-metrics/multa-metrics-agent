from src.models.hardware_telemetry.cpu import CpuMixedStats, CpuStats, CpuTimes
from src.models.hardware_telemetry.storage import DiskGeneralStats, DiskIoCounters
from src.models.hardware_telemetry.network import NetworkIoCounters, NetworkGeneralStats
from src.models.hardware_telemetry.ram import RamVirtualMemory, RamMemorySwap


cpu_times_model = CpuTimes()
cpu_times_model.retrieve()
parsed_cpu_times_model = cpu_times_model.to_dict()

cpu_stats_model = CpuStats()
cpu_stats_model.retrieve()
parsed_cpu_stats_model = cpu_stats_model.to_dict()

cpu_mixed_stats_model = CpuMixedStats()
cpu_mixed_stats_model.retrieve()
parsed_cpu_mixed_stats_model = cpu_mixed_stats_model.to_dict()

disk_general_stats_model = DiskGeneralStats()
disk_general_stats_model.retrieve()
parsed_disk_general_stats_model = disk_general_stats_model.to_dict()

disk_io_counters_model = DiskIoCounters()
disk_io_counters_model.retrieve()
parsed_disk_io_counters_model = disk_io_counters_model.to_dict()

network_io_counters_model = NetworkIoCounters()
network_io_counters_model.retrieve()
parsed_network_io_counters_model = network_io_counters_model.to_dict()

network_general_stats_model = NetworkGeneralStats()
network_general_stats_model.retrieve()
parsed_network_general_stats_model = network_general_stats_model.to_dict()

ram_virtual_model = RamVirtualMemory()
ram_virtual_model.retrieve()
parsed_ram_virtual_model = ram_virtual_model.to_dict()

ram_swap_model = RamMemorySwap()
ram_swap_model.retrieve()
parsed_ram_swap_model = ram_swap_model.to_dict()

response = {
    "cpu": {
        "stats": parsed_cpu_stats_model,
        "times": parsed_cpu_times_model,
        "mixed_stats": parsed_cpu_mixed_stats_model
    },
    "network": {
        "stats": parsed_network_general_stats_model,
        "io_counters": parsed_network_io_counters_model
    },
    "ram": {
        "virtual": parsed_ram_virtual_model,
        "swap": parsed_ram_swap_model
    },
    "storage": {
        "stats": parsed_disk_general_stats_model,
        "io_counters": parsed_disk_io_counters_model
    }
}

print("End")
