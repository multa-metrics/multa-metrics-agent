from src.models.hardware_telemetry.base import BaseHardware


class RamVirtualMemory(BaseHardware):
    class Meta:
        model_key = "ram_memory"
        data_function = "virtual_memory"
        attributes = ["total", "available", "percent", "used", "free", "shared", "buffers", "cached"]

    def __init__(self, shared_memory_instance=None):
        super(RamVirtualMemory, self).__init__(shared_memory_instance)

    def __str__(self):
        return "RAM Memory - Virtual"


class RamMemorySwap(BaseHardware):
    class Meta:
        model_key = "ram_swap_memory"
        data_function = "swap_memory"
        attributes = ["total", "used", "free", "percent"]

    def __init__(self, shared_memory_instance=None):
        super(RamMemorySwap, self).__init__(shared_memory_instance)

    def __str__(self):
        return "RAM Memory - Swap"
