import traceback

from src.models.hardware_telemetry.cpu import CpuMixedStats, CpuStats, CpuTimes
from src.models.hardware_telemetry.storage import DiskGeneralStats, DiskIoCounters
from src.models.hardware_telemetry.network import NetworkIoCounters, NetworkGeneralStats
from src.models.hardware_telemetry.ram import RamVirtualMemory, RamMemorySwap


class HardwareStatsRealTimeRetrieve:
    def __init__(self):
        self.cpu_times_model = CpuTimes()
        self.cpu_stats_model = CpuStats()
        self.cpu_mixed_stats_model = CpuMixedStats()
        self.disk_general_stats_model = DiskGeneralStats()
        self.disk_io_counters_model = DiskIoCounters()
        self.network_io_counters_model = NetworkIoCounters()
        self.network_general_stats_model = NetworkGeneralStats()
        self.ram_virtual_model = RamVirtualMemory()
        self.ram_swap_model = RamMemorySwap()

        self.cpu_data = {}
        self.network_data = {}
        self.ram_data = {}
        self.storage_data = {}

    def get_cpu(self):
        cpu_data = {
            "stats": None,
            "times": None,
            "mixed_stats": None
        }
        try:
            self.cpu_stats_model.retrieve()
            self.cpu_times_model.retrieve()
            self.cpu_mixed_stats_model.retrieve()

            cpu_data["stats"] = self.cpu_stats_model.to_dict()
            cpu_data["times"] = self.cpu_times_model.to_dict()
            cpu_data["mixed_stats"] = self.cpu_mixed_stats_model.to_dict()

        except Exception:
            print("Error getting CPU data...")
            print(traceback.format_exc())

        return cpu_data

    def get_network(self):
        network_data = {
            "stats": None,
            "io_counters": None
        }
        try:
            self.network_general_stats_model.retrieve()
            self.network_io_counters_model.retrieve()

            network_data["stats"] = self.network_general_stats_model.to_dict()
            network_data["io_counters"] = self.network_io_counters_model.to_dict()

        except Exception:
            print("Error getting Network data...")
            print(traceback.format_exc())

        return network_data

    def get_ram(self):
        ram_data = {
            "virtual": None,
            "swap": None
        }
        try:
            self.ram_virtual_model.retrieve()
            self.ram_swap_model.retrieve()

            ram_data["virtual"] = self.ram_virtual_model.to_dict()
            ram_data["swap"] = self.ram_virtual_model.to_dict()

        except Exception:
            print("Error getting RAM data...")
            print(traceback.format_exc())

        return ram_data

    def get_storage(self):
        storage_data = {
            "stats": None,
            "io_counters": None
        }
        try:
            self.disk_general_stats_model.retrieve()
            self.disk_io_counters_model.retrieve()

            storage_data["stats"] = self.disk_general_stats_model.to_dict()
            storage_data["io_counters"] = self.disk_io_counters_model.to_dict()

        except Exception:
            print("Error getting Storage data...")
            print(traceback.format_exc())

        return storage_data

    def get_all(self):
        data = {
            "cpu": None,
            "network": None,
            "ram": None,
            "storage": None,
        }
        try:
            data["cpu"] = self.get_cpu()
            data["network"] = self.get_network()
            data["ram"] = self.get_ram()
            data["storage"] = self.get_storage()

        except Exception:
            print("Error getting overall stats")
            print(traceback.format_exc())

        return data
