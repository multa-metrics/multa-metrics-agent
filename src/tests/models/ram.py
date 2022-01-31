from src.models.hardware_telemetry.ram import RamVirtualMemory, RamMemorySwap


ram_virtual_model = RamVirtualMemory()
ram_virtual_model.retrieve()
parsed_ram_virtual_model = ram_virtual_model.to_dict()

ram_swap_model = RamMemorySwap()
ram_swap_model.retrieve()
parsed_ram_swap_model = ram_swap_model.to_dict()