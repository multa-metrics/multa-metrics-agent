from datetime import datetime
import platform
import subprocess
import sys
import time
import traceback
import psutil

from src.handlers.logging_handler import Logger
from src.handlers.utils import get_size, read_file, write_file
from src.settings.hardware import (
    BOOT_THRESHOLD,
    CPU_ANALYSIS_TIME,
    CPU_THRESHOLD,
    HDD_THRESHOLD,
    RAM_THRESHOLD,
    TEMPERATURE_THRESHOLD,
    BATTERY_THRESHOLD,
)


logs_handler = Logger()
logger = logs_handler.get_logger()


def get_shadow_data():
    shadow_data_dict = dict()
    real_time_data = get_real_time_data_system_metrics()
    system_info_data = get_system_info()

    for key, value in real_time_data.items():
        shadow_data_dict[key] = value

    for key, value in system_info_data.items():
        shadow_data_dict[key] = value

    return shadow_data_dict


def get_time_series_system_metrics():
    data_handler = HwAnalyzer()
    return_dict = {
        "ram_info": data_handler.get_ram_info(),
        "cpu_info": data_handler.get_cpu_dynamic_info(detailed=True),
        "disk_info": data_handler.get_disk_info(detailed=True),
        "temp_info": data_handler.get_temperature_info(detailed=True),
        "boot_time_info": data_handler.get_boottime_info(detailed=True),
        # "network_info": data_handler.get_network_info(),
        # "bw_info": data_handler.get_bandwidth_usage(detailed=True),
    }
    return return_dict


def get_real_time_data_system_metrics():
    data_handler = HwAnalyzer()
    return_dict = {
        "ram_info": data_handler.get_ram_info(),
        "cpu_dynamic_info": data_handler.get_cpu_dynamic_info(detailed=True),
        "disk_dynamic_info": data_handler.get_disk_info(detailed=True),
        "temp_info": data_handler.get_temperature_info(detailed=True),
        "boot_time_info": data_handler.get_boottime_info(detailed=True),
        "battery_info": {},
        "fans_info": {},
        # "network_info": data_handler.get_network_info(),
        # "bw_info": data_handler.get_bandwidth_usage(detailed=True),
    }
    return return_dict


def get_system_info():
    return_dict = {
        "hardware": HwInfo.get_physical_hardware_info(),
        "platform": HwInfo.get_static_platform_info(),
        "cpu_static_info": HwInfo.get_cpu_static_info(),
        "disk_static_nfo": HwInfo.get_static_disk_info(),
    }
    return return_dict


def get_system_metrics(extra_sensors=False):
    system_data = HwAnalyzer()
    return_dict = {}

    if extra_sensors is True:
        return_dict["battery"] = {
            "current": system_data.get_systems_peripherics_status()[1],
            "total": system_data.get_systems_peripherics_status()[1],
            "percentage": system_data.get_systems_peripherics_status()[1],
            "status": system_data.get_systems_peripherics_status()[1],
        }
        return_dict["fans"] = {
            "current": system_data.get_systems_peripherics_status()[0],
            "total": None,
            "percentage": None,
            "status": None,
        }

    return return_dict


class HwInfo:
    def __init__(self):
        pass

    @staticmethod
    def get_static_platform_info():
        platform_static_info = dict(
            system="", node="", release="", version="", machine="", processor="", architecture="", libc_version=""
        )
        try:
            platform_static_info["system"] = platform.system()
            platform_static_info["node"] = platform.node()
            platform_static_info["release"] = platform.release()
            platform_static_info["version"] = platform.version()
            platform_static_info["architecture"] = platform.architecture()[0]
            platform_static_info["libc_version"] = " ".join(platform.libc_ver())

        except Exception:
            logger.error(traceback.format_exc())

        return platform_static_info

    @staticmethod
    def get_physical_hardware_info():
        try:
            if sys.platform.startswith("darwin"):
                name = "Darwin-like"
            elif sys.platform.startswith("linux"):
                name = subprocess.call(["lscpu"])
            elif sys.platform.startswith("win32"):
                name = subprocess.call(["wmic", "cpu", "get", "name"])
            else:
                name = "-"

            physical_hardware_info = {"machine": platform.machine(), "processor": platform.processor(), "name": name}

        except Exception:
            logger.error("Can't read Physical Hardware Info")
            logger.error(traceback.format_exc())
            physical_hardware_info = {"machine": "-", "processor": "-", "name": "-"}

        return physical_hardware_info

    @staticmethod
    def get_cpu_static_info():
        cpu_static_dict = dict(
            physical_cpu_count=0,
            logical_cpu_count=0,
            cpu_affinity=0,
            min_cpu_freq=0,
            max_cpu_freq=0,
            per_cpu_freq=list(),
        )
        try:
            general_cpu_freq = psutil.cpu_freq(percpu=False)
            per_cpu_freq = psutil.cpu_freq(percpu=True)
            cpu_static_dict["physical_cpu_count"] = psutil.cpu_count(logical=False)
            cpu_static_dict["logical_cpu_count"] = psutil.cpu_count(logical=True)
            cpu_static_dict["min_cpu_freq"] = round(general_cpu_freq.min)
            cpu_static_dict["max_cpu_freq"] = round(general_cpu_freq.max)
            cpu_static_dict["per_cpu_freq"] = [dict(min=round(cpu.min), max=round(cpu.max)) for cpu in per_cpu_freq]

            try:
                cpu_static_dict["cpu_affinity"] = len(psutil.Process().cpu_affinity())
            except Exception:
                cpu_static_dict["cpu_affinity"] = 0

        except Exception:
            logger.error(traceback.format_exc())

        return cpu_static_dict

    @staticmethod
    def get_static_disk_info():
        disk_static_dict = dict(partitions_info=dict())
        try:
            partitions_info = psutil.disk_partitions()
            for partition in partitions_info:
                disk_static_dict["partitions_info"][partition.mountpoint] = dict(
                    device=partition.device, fstype=partition.fstype, opts=partition.opts
                )
        except Exception:
            logger.error(traceback.format_exc())

        return disk_static_dict


class HwAnalyzer:
    def __init__(self):
        pass

    @staticmethod
    def get_ram_info(detailed=True):
        ram_info_data = dict(
            raw=dict(
                memory=dict(total=0, available=0, percent=0, used=0, free=0, shared=0, buffers=0, cached=0),
                swap=dict(total=0, used=0, free=0, percent=0),
            ),
            insights=dict(current=0, total=0, percent=0, status=False),
        )
        try:
            memory_data = psutil.virtual_memory()
            swap_data = psutil.swap_memory()

            ram_current_insight = getattr(memory_data, "total", 0) - getattr(memory_data, "available", 0)
            if ram_current_insight <= 0:
                ram_current_insight = 0

            ram_info_data["raw"]["memory"]["total"] = getattr(memory_data, "total", 0)
            ram_info_data["raw"]["memory"]["available"] = getattr(memory_data, "available", 0)
            ram_info_data["raw"]["memory"]["percent"] = getattr(memory_data, "percent", 0)
            ram_info_data["raw"]["memory"]["used"] = getattr(memory_data, "used", 0)
            ram_info_data["raw"]["memory"]["free"] = getattr(memory_data, "free", 0)
            ram_info_data["raw"]["memory"]["shared"] = getattr(memory_data, "shared", 0)
            ram_info_data["raw"]["memory"]["buffers"] = getattr(memory_data, "buffers", 0)
            ram_info_data["raw"]["memory"]["cached"] = getattr(memory_data, "cached", 0)
            ram_info_data["raw"]["swap"]["total"] = getattr(swap_data, "total", 0)
            ram_info_data["raw"]["swap"]["used"] = getattr(swap_data, "used", 0)
            ram_info_data["raw"]["swap"]["free"] = getattr(swap_data, "free", 0)
            ram_info_data["raw"]["swap"]["percent"] = getattr(swap_data, "percent", 0)
            ram_info_data["insights"]["current"] = ram_current_insight
            ram_info_data["insights"]["total"] = getattr(memory_data, "cached", 0)
            ram_info_data["insights"]["percent"] = getattr(memory_data, "cached", 0)
            ram_info_data["insights"]["status"] = True if getattr(memory_data, "percent", 0) > RAM_THRESHOLD else False

        except Exception:
            logger.error("Can't get RAM info from system...")
            logger.error(traceback.format_exc())

        return ram_info_data

    @staticmethod
    def get_cpu_dynamic_info(detailed=True):
        cpu_info_dict = dict(
            raw=dict(percent_per_cpu=list(), freq_per_cpu=list(), avg_load_times=list(),),
            insights=dict(percent=0, high=False,),
        )
        try:
            cpu_percent_list = psutil.cpu_percent(interval=CPU_ANALYSIS_TIME, percpu=True)
            cpu_info_dict["insights"]["percent"] = round(sum(cpu_percent_list) / len(cpu_percent_list))
            cpu_info_dict["insights"]["high"] = True if cpu_info_dict["insights"]["percent"] >= CPU_THRESHOLD else False

            if detailed is True:
                cpu_count = psutil.cpu_count()
                cpu_freq_list = psutil.cpu_freq(percpu=True)
                cpu_avg_load_list = psutil.getloadavg()
                cpu_info_dict["raw"]["percent_per_cpu"] = [round(cpu) for cpu in cpu_percent_list]
                cpu_info_dict["raw"]["freq_per_cpu"] = [round(cpu_freq.current) for cpu_freq in cpu_freq_list]
                cpu_info_dict["raw"]["avg_load_times"] = [round(avg_load) for avg_load in cpu_avg_load_list]
                cpu_info_dict["raw"]["avg_load_percent_times"] = [
                    round(aload / cpu_count * 100) for aload in cpu_avg_load_list
                ]

        except Exception:
            logger.error(traceback.format_exc())

        return cpu_info_dict

    @staticmethod
    def get_disk_info(detailed=True):
        disk_info_dict = dict(
            current=0,
            total=0,
            percent=0,
            high=False,
            general_io=dict(read_count=0, write_count=0, read_bytes=0, write_bytes=0, read_time=0, write_time=0),
        )
        try:
            disk_info = psutil.disk_usage(path="/")
            disk_info_dict["current"] = getattr(disk_info, "used", 0)
            disk_info_dict["total"] = getattr(disk_info, "total", 0)
            disk_info_dict["percent"] = round(getattr(disk_info, "percent", 0))
            disk_info_dict["high"] = True if getattr(disk_info, "percent", 0) >= HDD_THRESHOLD else False

            general_disk_io_counters = psutil.disk_io_counters(perdisk=False)
            disk_info_dict["general_io"]["read_count"] = getattr(general_disk_io_counters, "read_count", 0)
            disk_info_dict["general_io"]["write_count"] = getattr(general_disk_io_counters, "write_count", 0)
            disk_info_dict["general_io"]["read_bytes"] = getattr(general_disk_io_counters, "read_bytes", 0)
            disk_info_dict["general_io"]["write_bytes"] = getattr(general_disk_io_counters, "write_bytes", 0)
            disk_info_dict["general_io"]["read_time"] = getattr(general_disk_io_counters, "read_count", 0)
            disk_info_dict["general_io"]["write_time"] = getattr(general_disk_io_counters, "write_time", 0)

            """
            if detailed is True:
                specific_disk_io_counters = psutil.disk_io_counters(perdisk=True)
                hdd_drives_identifiers = HDD_DRIVES.split(",")
                for drive in hdd_drives_identifiers:
                    specific_disk_io_counters_ = specific_disk_io_counters.get(drive, dict())
                    disk_info_dict["specific_io"][drive] = dict()
                    disk_info_dict["specific_io"][drive]["read_count"] = getattr(specific_disk_io_counters_, "read_count",
                                                                                 0)
                    disk_info_dict["specific_io"][drive]["write_count"] = getattr(specific_disk_io_counters_, "write_count",
                                                                                  0)
                    disk_info_dict["specific_io"][drive]["read_bytes"] = getattr(specific_disk_io_counters_, "read_bytes",
                                                                                 0)
                    disk_info_dict["specific_io"][drive]["write_bytes"] = getattr(specific_disk_io_counters_, "write_bytes",
                                                                                  0)
                    disk_info_dict["specific_io"][drive]["read_time"] = getattr(specific_disk_io_counters_, "read_time", 0)
                    disk_info_dict["specific_io"][drive]["write_time"] = getattr(specific_disk_io_counters_, "write_time",
                                                                                 0)
            """

        except Exception:
            logger.error(traceback.format_exc())

        return disk_info_dict

    @staticmethod
    def get_boottime_info(detailed=True):
        boot_time_dict = dict(
            raw=dict(last_boot_timestamp=0, current_date=""),
            insights=dict(last_boot="", days_since_boot=0, seconds_since_boot=0, high=False),
        )
        try:
            boot_time_data = psutil.boot_time()
            boot_date = datetime.fromtimestamp(boot_time_data)
            current_date = datetime.now()

            boot_time_dict["insights"]["last_boot"] = str(boot_date)
            boot_time_dict["insights"]["days_since_boot"] = (current_date - boot_date).days
            boot_time_dict["insights"]["seconds_since_boot"] = round(time.time() - psutil.boot_time())
            boot_time_dict["insights"]["high"] = (
                True if boot_time_dict["insights"]["days_since_boot"] > BOOT_THRESHOLD else False
            )

            if detailed is True:
                boot_time_dict["raw"]["last_boot_timestamp"] = boot_time_data
                boot_time_dict["raw"]["current_date"] = str(current_date)

        except Exception:
            logger.error(traceback.format_exc())

        return boot_time_dict

    @staticmethod
    def get_temperature_info(detailed=True):
        temperature_info_dict = dict(raw=dict(current=0, total=0), insights=dict(percent=0, high=False,),)
        if detailed is True:
            temperature_info_dict["raw"]["per_core"] = dict()

        try:
            if hasattr(psutil, "sensors_temperatures") is False:
                # logger.info("Unable to get temperature info from this OS")
                return temperature_info_dict
            base_temperature_info = psutil.sensors_temperatures(fahrenheit=True)
            temperature_info = base_temperature_info["coretemp"]

            # Getting current usage
            current_usage = list()
            for core in temperature_info:
                current_usage.append(core.current)

            # Getting maximum usage
            all_equal = all(core.high == temperature_info[0].high for core in temperature_info)
            if all_equal is True:
                high_temperature_average = temperature_info[0].high

            else:
                max_temps = []
                for core in temperature_info:
                    max_temps.append(core.high)
                high_temperature_average = sum(max_temps) / len(max_temps)

            temperature_info_dict["raw"]["current"] = round(sum(current_usage) / len(current_usage))
            temperature_info_dict["raw"]["total"] = round(high_temperature_average)
            temperature_info_dict["insights"]["percent"] = round(
                (temperature_info_dict["raw"]["current"] / temperature_info_dict["raw"]["total"]) * 100
            )
            temperature_info_dict["insights"]["high"] = (
                True if temperature_info_dict["insights"]["percent"] >= TEMPERATURE_THRESHOLD else False
            )

            if detailed is True:
                for core, values in base_temperature_info.items():
                    temperature_info_dict["raw"]["per_core"][core] = list()
                    for data in values:
                        temperature_info_dict["raw"]["per_core"][core].append(
                            dict(
                                label=data.label,
                                current=round(data.current),
                                high=round(data.high),
                                critical=round(data.critical),
                            )
                        )

        except Exception:
            logger.error(traceback.format_exc())

        return temperature_info_dict

    # ------------------------------------------------ other_peripherics_data ---------------------------------------
    @staticmethod
    def get_systems_peripherics_status():
        """
        Gets fans speed in RPM and data from Battery as: charge, time_left, status, plugged in
        TODO: continue reviewing if we can be able to get to power consumption or the voltage, or something like that
        """
        try:
            sensor_info_dict = {
                "battery": {
                    "raw": {"percent": 0, "time_left": 0, "plugged": False, "power": 0},
                    "insights": {"status": False},
                },
                "fans": {"raw": {"speed": 0}, "insights": {}},
            }
            # Verifying sensors_fans support platform
            fans = 0
            if hasattr(psutil, "sensors_fans") is True:
                fans = psutil.sensors_fans()
                if not fans:
                    sensor_info_dict["fans"]["raw"]["speed"] = 0

            # Verifying battery support platform
            battery = 0
            if hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if not battery:
                    sensor_info_dict = {
                        "battery": {
                            "raw": {"percent": 0, "time_left": 0, "plugged": False, "power": 0},
                            "insights": {"status": False},
                        }
                    }

            # Battery.
            if battery:
                battery_percent = round(battery.percent, 2)
                if battery.power_plugged:
                    battery_status = False if battery.percent < BATTERY_THRESHOLD else True
                    battery_plugged = True
                    battery_time_left = 0
                else:
                    battery_status = False if battery.percent < BATTERY_THRESHOLD else True
                    battery_plugged = False
                    battery_time_left = battery.secsleft

                sensor_info_dict = {
                    "battery": {
                        "raw": {
                            "percent": battery_percent,
                            "time_left": battery_time_left,
                            "plugged": battery_plugged,
                            "power": 0,
                        },
                        "insights": {"status": battery_status},
                    },
                    "fans": {"raw": {"speed": fans}, "insights": {}},
                }
                return sensor_info_dict

        except Exception:
            logger.error("Some errors where find about system peripheries status")
            logger.error(traceback.format_exc())

        return sensor_info_dict

    # ------------------------------------------------ interface_data ---------------------------------------
    @staticmethod
    def get_bandwidth_usage(detailed=True):
        bandwidth_usage = dict(current=0)
        try:
            # loading old value
            old_data = read_file()
            old_value = old_data["old_value"]
            old_time = old_data["old_time"]

            new_value = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
            new_time = time.time()

            bandwidth = (new_value - old_value) / (new_time - old_time)

            # to written new value in the file
            new_data = {"old_value": new_value, "old_time": new_time}
            write_file(new_data)

            bandwidth_usage["current"] = round(bandwidth, 2)
            return bandwidth_usage

        except Exception:
            logger.error("Some errors occurs getting bandwidth usage")
            logger.error(traceback.format_exc())

        return bandwidth_usage

    # ------------------------------------------------ network_info ---------------------------------------

    @staticmethod
    def get_network_info():
        """
        Return the network info like the following example:
            === Interface: Ethernet ===
              IP Address: 169.254.219.199
              Netmask: 255.255.0.0
              Broadcast IP: None
            === Interface: Ethernet 5 ===
            IP Address: 169.254.83.69
              Netmask: 255.255.0.0
              Broadcast IP: None
            === Interface: Conexión de área local* 1 ===
              IP Address: 169.254.121.124
              Netmask: 255.255.0.0
              Broadcast IP: None
            === Interface: Conexión de área local* 3 ===
              IP Address: 169.254.218.24
              Netmask: 255.255.0.0
            Broadcast IP: None
            === Interface: Wi-Fi ===
              IP Address: 192.168.0.157
              Netmask: 255.255.255.0
              Broadcast IP: None
            === Interface: Loopback Pseudo-Interface 1 ===
              IP Address: 127.0.0.1
              Netmask: 255.0.0.0
              Broadcast IP: None
            === Interface: Loopback Pseudo-Interface 1 ===
            Total Bytes Sent: 2.65GB
            Total Bytes Received: 30.66GB
        """
        # TODO: REVIEW NETWORK INFO
        try:
            # Network information
            logger.info("=" * 40, "Network Information", "=" * 40)
            # get all network interfaces (virtual and physical)
            if_addrs = psutil.net_if_addrs()
            for interface_name, interface_addresses in if_addrs.items():
                for address in interface_addresses:
                    logger.info(f"=== Interface: {interface_name} ===")
                    if str(address.family) == "AddressFamily.AF_INET":
                        logger.info(f"  IP Address: {address.address}")
                        logger.info(f"  Netmask: {address.netmask}")
                        logger.info(f"  Broadcast IP: {address.broadcast}")
                    elif str(address.family) == "AddressFamily.AF_PACKET":
                        logger.info(f"  MAC Address: {address.address}")
                        logger.info(f"  Netmask: {address.netmask}")
                        logger.info(f"  Broadcast MAC: {address.broadcast}")
            # get IO statistics since boot
            net_io = psutil.net_io_counters()
            logger.info(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
            logger.info(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")

        except Exception:
            logger.error("Error getting network data...")
            logger.error(traceback.format_exc())
