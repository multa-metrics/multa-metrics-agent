from src.models.hardware_telemetry.base import BaseHardware


class CpuTimes(BaseHardware):
    class Meta:
        model_key = "cpu_times"
        data_function = "cpu_times"
        attributes = ["user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal", "guest", "guest_nice"]
        extra_advanced_fields = [
            {
                "name": "cpu_times_percent",
                "function": "cpu_times_percent",
                "kwargs": {
                    "interval": 2,
                    "percpu": True
                }
            }
        ]

    def __init__(self, shared_memory_instance=None):
        super(CpuTimes, self).__init__(shared_memory_instance)

    def __str__(self):
        return "CPU Times"


class CpuStats(BaseHardware):
    class Meta:
        model_key = "cpu_stats"
        data_function = "cpu_stats"
        attributes = ["ctx_switches", "interrupts", "soft_interrupts", "syscalls"]

    def __init__(self, shared_memory_instance=None):
        super(CpuStats, self).__init__(shared_memory_instance)

    def __str__(self):
        return "CPU Native Statistics"


class CpuMixedStats(BaseHardware):
    class Meta:
        model_key = "cpu_mixed_stats"
        extra_advanced_fields = [
            {
                "name": "cpu_percent",
                "function": "cpu_percent",
                "kwargs": {
                    "interval": 2,
                    "percpu": True
                }
            },
            {
                "name": "cpu_count_physical",
                "function": "cpu_count",
                "kwargs": {
                    "logical": False
                }
            },
            {
                "name": "cpu_count_logical",
                "function": "cpu_count",
                "kwargs": {
                    "logical": True
                }
            },
            {
                "name": "cpu_frequency",
                "function": "cpu_freq",
                "kwargs": {
                    "percpu": True
                }
            },
            {
                "name": "load_average",
                "function": "getloadavg",
            }
        ]

    def __init__(self, shared_memory_instance=None):
        super(CpuMixedStats, self).__init__(shared_memory_instance)
        self.load_average_percent = None

    def __str__(self):
        return "CPU Mixed Statistics"

    def parse(self):
        self.load_average_percent = [x / self.cpu_count_logical * 100 for x in self.load_average]
