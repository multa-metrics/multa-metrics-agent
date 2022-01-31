import os, sys
sys.path.append("/workspaces/multa-metrics-agent")

import json
import time

from src.controllers.hardware_data_collection import HardwareStatsCollect
from src.models.shared_memory import SharedMemory


class Service:
    def __init__(self):
        self.shared_memory = SharedMemory()

        self.hardware_stats_collection_controller = HardwareStatsCollect(shared_memory_instance=self.shared_memory)
        
        # TODO: Add views to retrieve data from Shared Memory.
        # TODO: Add view to retrieve data and process to get Device Defender data.

    def start(self):
        self.hardware_stats_collection_controller.start()


if __name__ == "__main__":
    service_handler = Service()
    service_handler.start()

    while True:
        print(f"Analysis trace - {time.time()}")
        print(service_handler.shared_memory.shared_memory)
        time.sleep(5)
