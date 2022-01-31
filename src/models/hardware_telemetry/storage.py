import psutil

from src.models.hardware_telemetry.base import BaseHardware


class DiskIoCounters(BaseHardware):
    class Meta:
        model_key = "disk_io_counters"
        data_function = "disk_io_counters"
        attributes = [
            "read_count",
            "write_count",
            "read_bytes",
            "write_bytes",
            "read_time",
            "write_time",
            "busy_time",
            "read_merged_count",
            "write_merged_count"
        ]

    def __init__(self, shared_memory_instance=None):
        super(DiskIoCounters, self).__init__(shared_memory_instance)

    def __str__(self):
        return "Disk I/O Counters"


class DiskGeneralStats(BaseHardware):
    class Meta:
        model_key = "disk_general_stats"
        extra_advanced_fields = [
            {
                "name": "disk_partitions_physical",
                "function": "disk_partitions",
            },
            {
                "name": "disk_partitions_logical",
                "function": "disk_partitions",
                "kwargs": {
                    "all": True
                }
            },
            {
                "name": "disk_io_counters_overall",
                "function": "disk_io_counters",
                "kwargs": {
                    "perdisk": False,
                    "nowrap": True
                }
            },
            {
                "name": "disk_io_counters_specific",
                "function": "disk_io_counters",
                "kwargs": {
                    "perdisk": True,
                    "nowrap": True
                }
            }
        ]

        fields_include = ["disk_partitions_logical_stats", "disk_partitions_physical_stats"]
        fields_exclude = ["disk_partitions_logical", "disk_partitions_physical"]

    def __init__(self, shared_memory_instance=None):
        super(DiskGeneralStats, self).__init__(shared_memory_instance)

    def __str__(self):
        return "Disk General Stats"

    def parse(self):
        self.disk_partitions_physical_stats = {}

        for disk in self.disk_partitions_physical:
            self.disk_partitions_physical_stats[disk.device] = {}
            self.disk_partitions_physical_stats[disk.device]["usage"] = dict(psutil.disk_usage(disk.mountpoint)._asdict())
            self.disk_partitions_physical_stats[disk.device].update(dict(disk._asdict()))

        self.disk_partitions_logical_stats = {}

        for disk in self.disk_partitions_logical:
            self.disk_partitions_logical_stats[disk.device] = {}
            try:
                self.disk_partitions_logical_stats[disk.device]["usage"] = dict(psutil.disk_usage(disk.mountpoint)._asdict())
            except Exception:
                self.disk_partitions_logical_stats[disk.device]["usage"] = None

            self.disk_partitions_logical_stats[disk.device].update(dict(disk._asdict()))
