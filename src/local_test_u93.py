import json

from src.handlers.hardware_handler import (
    HwAnalyzer,
    HwInfo,
    get_real_time_data_system_metrics,
    get_shadow_data,
)


# ram_data = {"test": {"second_level": get_ram_info()}}
# print(ram_data)

# cpu_data = get_cpu_info()
# print(cpu_data)

# disk_data = get_disk_info()
# print(disk_data)

# system_info = get_system_info()
# print(system_info)


# def flatten_dict(dd, separator="_", prefix=""):
#     return (
#         {
#             prefix + separator + k if prefix else k: v
#             for kk, vv in dd.items()
#             for k, v in flatten_dict(vv, separator, kk).items()
#         }
#         if isinstance(dd, dict)
#         else {prefix: dd}
#     )
#
#
# print(flatten_dict(ram_data))

# info = HwAnalyzer.get_temperature_info(detailed=True)
# print(info)
#
# print(get_real_time_data_system_metrics())
# print(get_system_info())

shadow_data = get_shadow_data()
print(json.dumps(shadow_data, indent=4))
