import psutil
import json
import datetime
from datetime import datetime
import wmi
import time
import subprocess
import timeit
from uptime import uptime
import power
from datetime import timedelta
import platform, subprocess, sys, os

from src.handlers.hardware_handler import (
    HwAnalyzer,
    HwInfo,
    get_real_time_data_system_metrics,
    get_shadow_data,
    get_system_info,
)

# data = get_system_metrics()
# print(data)


def avg(value_list):
    num = 0
    length = len(value_list)
    for val in value_list:
        num += val
    final_value = num / length
    return final_value


def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor


print("\n-------ninth test------")


print("\n-------eighth test------")

# Network information
print("=" * 40, "Network Information", "=" * 40)
# get all network interfaces (virtual and physical)
if_addrs = psutil.net_if_addrs()
for interface_name, interface_addresses in if_addrs.items():
    for address in interface_addresses:
        print(f"=== Interface: {interface_name} ===")
        if str(address.family) == "AddressFamily.AF_INET":
            print(f"  IP Address: {address.address}")
            print(f"  Netmask: {address.netmask}")
            print(f"  Broadcast IP: {address.broadcast}")
        elif str(address.family) == "AddressFamily.AF_PACKET":
            print(f"  MAC Address: {address.address}")
            print(f"  Netmask: {address.netmask}")
            print(f"  Broadcast MAC: {address.broadcast}")
# get IO statistics since boot
net_io = psutil.net_io_counters()

print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")

print(f"\nnumber of packets recv: {get_size(net_io.packets_recv)}")

print(f"number of packets sent: {get_size(net_io.packets_sent)}")

print(f"\ntotal number of errors while sending: {get_size(net_io.errout)}")

print(f"\ntotal number of outgoing packets which were dropped: {get_size(net_io.dropout)}")

print(f"total number of incoming packets which were dropped: {get_size(net_io.dropin)}")


print("\n-------sixth test------")

"""
import sensors
sensors.init()
try:
    for chip in sensors.iter_detected_chips():
    print '%s at %s' % (chip, chip.adapter_name)
    for feature in chip:
    print '  %s: %.2f' % (feature.label, feature.get_value())
finally:
sensors.cleanup()
"""
print("\n-------fifth test------")

print("\n-------fourth test------")
"""
import sensors
sensors.init()
try:
    for chip in sensors.iter_detected_chips():
        print ('%s at %s' % (chip, chip.adapter_name))
            for feature in chip:
                print ('  %s: %.2f' % (feature.label, feature.get_value()))

finally:
sensors.cleanup()
"""

print("\n-------third test------")

print("\n-------second test------")


old_value = 0
# while True:
new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")
print(f"Total bandwidth: {get_size(new_value)}")

if old_value:
    print(f"Bandwidth dif : {get_size(new_value - old_value)}")

old_value = new_value

# time.sleep(2)


print("-------first test------")
"""
if not hasattr(psutil, "sensors_temperatures"):
    sys.exit("platform not supported")
temps = psutil.sensors_temperatures()
if not temps:
    sys.exit("can't read any temperature")
for name, entries in temps.items():
    print(name)
    for entry in entries:
        print(
            "%-20s %s °C (high = %s °C, critical = %s °C)"
            % (entry.label or name, entry.current, entry.high, entry.critical)
        )

"""

data = HwAnalyzer


data_1 = get_real_time_data_system_metrics()
print(f"Bandwidth : {data_1}")
