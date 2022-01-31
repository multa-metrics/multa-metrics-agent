import os, sys
print(":".join(sys.path))
sys.path.append("/Users/el_u93/Documents/multa-metrics-projects/multa-metrics-agent/")

import json
from src.models.hardware_telemetry.defender import DeviceDefenderCollector


device_defender_collector_model = DeviceDefenderCollector()
device_defender_collector_model.retrieve()
parsed_device_defender_collector_model = device_defender_collector_model.to_dict()

print(json.dumps(parsed_device_defender_collector_model, indent=4))

device_defender_collector_model.background_functions_run()
