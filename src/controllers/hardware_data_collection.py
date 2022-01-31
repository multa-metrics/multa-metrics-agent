import traceback

from src.models.hardware_telemetry.cpu import CpuMixedStats, CpuStats, CpuTimes
from src.models.hardware_telemetry.defender import DeviceDefenderCollector
from src.models.hardware_telemetry.network import NetworkIoCounters, NetworkGeneralStats
from src.models.hardware_telemetry.ram import RamVirtualMemory, RamMemorySwap
from src.models.hardware_telemetry.storage import DiskGeneralStats, DiskIoCounters

from src.settings.data_collection import HARDWARE_DATA_SAMPLE


class HardwareStatsCollect:
    def __init__(self, shared_memory_instance):
        self.shared_memory_instance = shared_memory_instance

        self.cpu_times_model = CpuTimes(self.shared_memory_instance)
        self.cpu_stats_model = CpuStats(self.shared_memory_instance)
        self.cpu_mixed_stats_model = CpuMixedStats(self.shared_memory_instance)
        self.device_defender_collector_model = DeviceDefenderCollector(self.shared_memory_instance)
        self.disk_general_stats_model = DiskGeneralStats(self.shared_memory_instance)
        self.disk_io_counters_model = DiskIoCounters(self.shared_memory_instance)
        self.network_io_counters_model = NetworkIoCounters(self.shared_memory_instance)
        self.network_general_stats_model = NetworkGeneralStats(self.shared_memory_instance)
        self.ram_virtual_model = RamVirtualMemory(self.shared_memory_instance)
        self.ram_swap_model = RamMemorySwap(self.shared_memory_instance)

    def configure_settings(self):
        self.cpu_times_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)
        self.cpu_stats_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)
        self.cpu_mixed_stats_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)
        self.device_defender_collector_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)
        self.disk_general_stats_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)
        self.disk_io_counters_model.configure_setting(
            "background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE
        )
        self.network_io_counters_model.configure_setting(
            "background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE
        )
        self.network_general_stats_model.configure_setting(
            "background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE
        )
        self.ram_virtual_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)
        self.ram_swap_model.configure_setting("background_shared_memory_store_frequency", HARDWARE_DATA_SAMPLE)

    def start(self):
        self.configure_settings()

        # Start background functions threads.
        self.device_defender_collector_model.background_functions_run()

        # Start Shared Memory collect functions threads.
        self.cpu_times_model.background_shared_memory_collect_start()
        self.cpu_stats_model.background_shared_memory_collect_start()
        self.cpu_mixed_stats_model.background_shared_memory_collect_start()
        self.device_defender_collector_model.background_shared_memory_collect_start()
        self.disk_general_stats_model.background_shared_memory_collect_start()
        self.disk_io_counters_model.background_shared_memory_collect_start()
        self.network_io_counters_model.background_shared_memory_collect_start()
        self.network_general_stats_model.background_shared_memory_collect_start()
        self.ram_virtual_model.background_shared_memory_collect_start()
        self.ram_swap_model.background_shared_memory_collect_start()
