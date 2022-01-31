import copy
import time
import traceback

from src.models.hardware_telemetry.base import BaseHardware


class NetworkIoCounters(BaseHardware):
    class Meta:
        model_key = "network_io_counters"
        data_function = "net_io_counters"
        attributes = [
            "bytes_sent",
            "bytes_recv",
            "packets_sent",
            "packets_recv",
            "errin",
            "errout",
            "dropin",
            "dropout",
        ]
        extra_advanced_fields = [
            {
                "name": "net_io_counters_specific",
                "function": "net_io_counters",
                "kwargs": {
                    "pernic": True,
                    "nowrap": True
                }
            },
        ]

    def __init__(self, shared_memory_instance=None):
        super(NetworkIoCounters, self).__init__(shared_memory_instance)

    def __str__(self):
        return "Network I/O Counters"


class NetworkGeneralStats(BaseHardware):
    class Meta:
        model_key = "network_general_stats"
        functions = []
        extra_advanced_fields = [
            {
                "name": "net_io_counters_specific",
                "function": "net_io_counters",
                "kwargs": {
                    "pernic": True,
                    "nowrap": True
                }
            },
            # {
            #     "name": "net_connections_inet",
            #     "function": "net_connections",
            #     "kwargs": {
            #         "kind": "inet",
            #     }
            # },
            # {
            #     "name": "net_connections",
            #     "function": "net_connections",
            #     "kwargs": {
            #         "kind": "all",
            #     }
            # },
            {
                "name": "net_if_addrs",
                "function": "net_if_addrs",
            },
            {
                "name": "net_if_stats",
                "function": "net_if_stats",
            }
        ]

        fields_include = ["net_aggregated_stats", "stats_per_second", "stats_per_minute"]
        # fields_exclude = ["disk_partitions_logical", "disk_partitions_physical"]
        background_functions = [
            {
                "name": "analyze_per_second"
            },
            {
                "name": "analyze_per_minute"
            }
        ]

    def __init__(self, shared_memory_instance=None):
        super(NetworkGeneralStats, self).__init__(shared_memory_instance)
        self.stats_per_second = None
        self.stats_per_minute = None

    def __str__(self):
        return "Network General Stats"

    def parse(self):
        self.net_aggregated_stats = {}
        for interface, data in self.net_io_counters_specific.items():
            self.net_aggregated_stats[interface] = {}
            self.net_aggregated_stats[interface]["io"] = data

        for interface, data in self.net_if_stats.items():
            self.net_aggregated_stats[interface]["if_stats"] = data

        for interface, data in self.net_if_addrs.items():
            self.net_aggregated_stats[interface]["if_addrs"] = data

    def collect_difference(self, current_stats):
        try:
            previous_net_per_second_aggregated_stats = copy.deepcopy(current_stats)

            self.retrieve()

            for interface, data in self.net_io_counters_specific.items():
                self.net_aggregated_stats[interface] = {}
                self.net_aggregated_stats[interface]["io"] = data

            for interface, data in self.net_if_stats.items():
                self.net_aggregated_stats[interface]["if_stats"] = data

            for interface, data in self.net_if_addrs.items():
                self.net_aggregated_stats[interface]["if_addrs"] = data

            current_net_per_second_aggregated_stats = self.to_dict()["net_io_counters_specific"]

            if previous_net_per_second_aggregated_stats != {}:
                network_stats_difference = self.calculate_diff(
                    current_net_per_second_aggregated_stats,
                    previous_net_per_second_aggregated_stats
                )
                return network_stats_difference, current_net_per_second_aggregated_stats

            else:
                return None, current_net_per_second_aggregated_stats

        except Exception:
            print("Error collecting network stats in the background...")
            print(traceback.format_exc())
            return None, current_stats

    def calculate_diff(self, d1, d2):
        diff = dict()
        for k, v1 in d1.items():
            if isinstance(v1, dict):
                diff[k] = self.calculate_diff(v1, d2[k])
            elif isinstance(v1, list):
                continue
            else:
                diff[k] = v1 - d2[k]

        return diff

    def analyze_per_second(self):
        print("Starting Analysis per second...")
        try:
            current_stats = {}
            while True:
                self.stats_per_second, current_stats = self.collect_difference(current_stats)
                time.sleep(1)
                print(self.to_dict())

        except Exception:
            print("Error analyzing per second...")
            print(traceback.format_exc())

    def analyze_per_minute(self):
        print("Starting Analysis per minute...")
        try:
            current_stats = {}
            while True:
                self.stats_per_minute, current_stats = self.collect_difference(current_stats)
                time.sleep(60)

        except Exception:
            print("Error analyzing per minute...")
            print(traceback.format_exc())
