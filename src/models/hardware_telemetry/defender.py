import copy
import socket
import time
import traceback

from src.models.hardware_telemetry.base import BaseHardware

from ipaddress import ip_address, IPv4Address
import psutil


class DeviceDefenderCollector(BaseHardware):
    class Meta:
        model_key = "device_defender_data"
        extra_advanced_fields = [
            {
                "name": "network_interfaces_addresses",
                "function": "net_if_addrs",
            },
            {
                "name": "network_connections",
                "function": "net_connections",
                "kwargs": {
                    "kind": "inet"
                }
            },
            {
                "name": "network_connections_tcp",
                "function": "net_connections",
                "kwargs": {
                    "kind": "tcp"
                }
            },
            {
                "name": "network_io_counters",
                "function": "net_io_counters",
                "kwargs": {
                    "pernic": False
                }
            },
            {
                "name": "network_interfaces_addresses",
                "function": "net_if_addrs",
            }
        ]

        fields_include = ["device_defender_data", "stats_per_second", "stats_per_minute"]

        background_functions = [
            {
                "name": "analyze_per_second"
            },
            {
                "name": "analyze_per_minute"
            }
        ]

    def __init__(self, shared_memory_instance=None):
        # TODO: Add parsing of device defender required metrics
        # TODO: Add parsing of device defender custom metrics

        super(DeviceDefenderCollector, self).__init__(shared_memory_instance)
        self.stats_per_second = None
        self.stats_per_minute = None
        self.device_defender_data = None

    def __str__(self):
        return "Device Defender Data"

    def parse(self):
        self.to_device_defender_data_dict()

    def get_interface_name(self, address):
        if address == "0.0.0.0" or address == "::":
            return address

        for interface in self.network_interfaces_addresses:
            for nic in self.network_interfaces_addresses[interface]:
                if nic.address == address:
                    return interface

    def parse_listening_tcp_ports(self):
        tcp_ports = list()
        for connection in self.network_connections:
            interface_ip_address = connection.laddr.ip
            interface_name = self.get_interface_name(interface_ip_address)
            
            if connection.status == "LISTEN" and connection.type == socket.SOCK_STREAM:
                if interface_name:
                    tcp_ports.append({"port": connection.laddr.port, "interface": interface_name})
                else:
                    tcp_ports.append({"port": connection.laddr.port})

        tcp_port_count = len(tcp_ports)
        return tcp_ports, tcp_port_count

    def parse_listening_udp_ports(self):
        udp_ports = list()
        for connection in self.network_connections:
            interface_ip_address = connection.laddr.ip
            interface_name = self.get_interface_name(interface_ip_address)
            
            if connection.type == socket.SOCK_DGRAM:
                if interface_name:
                    udp_ports.append({"port": connection.laddr.port, "interface": interface_name})
                else:
                    udp_ports.append({"port": connection.laddr.port})

        udp_port_count = len(udp_ports)
        return udp_ports, udp_port_count

    def parse_established_tcp_connections(self):
        remote_network_connections = list()

        protocols = ["tcp"]
        for protocol in protocols:
            for connection in self.network_connections_tcp:
                try:
                    if connection.status == "ESTABLISHED" or connection.status == "BOUND":
                        remote_address = connection.raddr.ip
                        remote_port = connection.raddr.port
                        local_address = connection.laddr.ip
                        interface_name = self.get_interface_name(local_address)
                        local_port = connection.laddr.port

                        if type(ip_address(remote_address)) is not IPv4Address:
                            remote_address = f"[{remote_address}]"

                        remote_connection = {
                            "local_interface": interface_name,
                            "local_port": local_port,
                            "remote_addr": f"{remote_address}:{remote_port}"
                        }
                        remote_network_connections.append(remote_connection)

                except Exception:
                    print(f"Error parsing network information protocol: {protocols}")
                    print(traceback.format_exc())

        remote_network_connections_count = len(remote_network_connections)
        return remote_network_connections, remote_network_connections_count

    def parse_custom_metrics(self):
        custom_metrics = dict()

        # Getting CPU Custom metric
        cpu_mixed_stats = self._shared_memory.shared_memory_model_read("cpu_mixed_stats")
        if cpu_mixed_stats is not None:
            # Analyzing CPU Percent metric
            cpu_percent = cpu_mixed_stats.get("cpu_percent", [])
            if len(cpu_percent) != 0:
                cpu_average = sum(cpu_percent) / len(cpu_percent)
                custom_metrics["cpu_average"]: [
                    {"number": round(cpu_average, 3)}
                ]
            
            # Analyzing CPU Load metric
            cpu_load_average_percent = cpu_mixed_stats.get("load_average", [])
            if len(cpu_load_average_percent) != 0:
                cpu_load_average = sum(cpu_load_average_percent) / len(cpu_load_average_percent)
                custom_metrics["cpu_load_average"]: [
                    {"number": round(cpu_load_average, 3)}
                ]

        return custom_metrics

    def to_device_defender_data_dict(self):
        if self.stats_per_second is None:
            return None

        listening_tcp_ports, listening_tcp_ports_total = self.parse_listening_tcp_ports()
        listening_udp_ports, listening_udp_ports_total = self.parse_listening_udp_ports()
        established_tcp_connections, established_tcp_connections_total = self.parse_established_tcp_connections()
        custom_metrics = self.parse_custom_metrics()

        self.device_defender_data = {
            "header": {
                "report_id": round(time.time()),
                "version": "1.0"
            },
            "metrics": {
                "listening_tcp_ports": {
                    "ports": listening_tcp_ports,
                    "total": listening_tcp_ports_total
                },
                "listening_udp_ports": {
                    "ports": listening_udp_ports,
                    "total": listening_udp_ports_total
                },
                "network_stats": copy.deepcopy(self.stats_per_second),
                "tcp_connections": {
                    "established_connections": {
                        "connections": established_tcp_connections,
                        "total": established_tcp_connections_total
                    }
                }
            },
            "custom_metrics": custom_metrics
        }

    def collect_difference(self, current_stats):
        try:
            previous_net_per_second_aggregated_stats = copy.deepcopy(current_stats)
            if current_stats == {}:
                parsed_previous_net_per_second_aggregated_stats = {}
            else:
                parsed_previous_net_per_second_aggregated_stats = {
                    "bytes_sent": previous_net_per_second_aggregated_stats.get("bytes_sent"),
                    "bytes_recv": previous_net_per_second_aggregated_stats.get("bytes_recv"),
                    "packets_sent": previous_net_per_second_aggregated_stats.get("packets_sent"),
                    "packets_recv": previous_net_per_second_aggregated_stats.get("packets_recv")
                }

            current_net_per_second_aggregated_stats = self.to_dict()["network_io_counters"]
            parsed_current_net_per_second_aggregated_stats = {
                "bytes_sent": current_net_per_second_aggregated_stats["bytes_sent"],
                "bytes_recv": current_net_per_second_aggregated_stats["bytes_recv"],
                "packets_sent": current_net_per_second_aggregated_stats["packets_sent"],
                "packets_recv": current_net_per_second_aggregated_stats["packets_recv"]
            }

            if parsed_previous_net_per_second_aggregated_stats != {}:
                network_stats_difference = self.calculate_diff(
                    parsed_current_net_per_second_aggregated_stats,
                    parsed_previous_net_per_second_aggregated_stats
                )
                return network_stats_difference, parsed_current_net_per_second_aggregated_stats

            else:
                return None, parsed_current_net_per_second_aggregated_stats

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
                self.retrieve()
                self.stats_per_second, current_stats = self.collect_difference(current_stats)
                time.sleep(1)

        except Exception:
            print("Error analyzing per second...")
            print(traceback.format_exc())

    # def background_shared_memory_collect(self):
    #     while True and isinstance(self.Meta.model_key, str) is True and isinstance(
    #             self.Meta.background_shared_memory_store_frequency, int
    #     ):
    #         self.retrieve()
    #         self._shared_memory.shared_memory_model_write(self.Meta.model_key, self.to_device_defender_data_dict())
    #
    #         time.sleep(self.Meta.background_shared_memory_store_frequency)