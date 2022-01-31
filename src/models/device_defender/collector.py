# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License").
#   You may not use this file except in compliance with the License.
#   A copy of the License is located at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   or in the "license" file accompanying this file. This file is distributed
#   on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
#   express or implied. See the License for the specific language governing
#   permissions and limitations under the License.


import psutil as ps
import socket
import metrics
import argparse
from time import sleep


class Collector(object):
    """
    Reads system information and populates a metrics object.

    This implementation utilizes `psutil <https://psutil.readthedocs.io/en/latest/>`_
    to make parsing metrics easier and more cross-platform.
    """

    def __init__(self, short_metrics_names=False):
        """
        Parameters
        ----------
        short_metrics_names : bool
                Toggle short object tags in output metrics.
        use_custom_metrics : bool
                Toggle whether to collect custom metrics.
        """
        # Keep a copy of the last metric, if there is one, so we can calculate change in some metrics.
        self._last_metric = None
        self._short_names = short_metrics_names

    @staticmethod
    def __get_interface_name(address):

        if address == '0.0.0.0' or address == '::':
            return address

        for iface in ps.net_if_addrs():
            for snic in ps.net_if_addrs()[iface]:
                if snic.address == address:
                    return iface

    def listening_ports(self, metrics):
        """
        Iterate over all inet connections in the LISTEN state and extract port and interface.
        """
        udp_ports = []
        tcp_ports = []
        for conn in ps.net_connections(kind='inet'):
            iface = Collector.__get_interface_name(conn.laddr.ip)
            if conn.status == "LISTEN" and conn.type == socket.SOCK_STREAM:
                if iface:
                    tcp_ports.append({'port': conn.laddr.port, 'interface': iface})
                else:
                    tcp_ports.append({'port': conn.laddr.port})
            if conn.type == socket.SOCK_DGRAM:  # on Linux, udp socket status is always "NONE"
                if iface:
                    udp_ports.append({'port': conn.laddr.port, 'interface': iface})
                else:
                    udp_ports.append({'port': conn.laddr.port})

        metrics.add_listening_ports("UDP", udp_ports)
        metrics.add_listening_ports("TCP", tcp_ports)

    @staticmethod
    def network_stats(metrics):
        net_counters = ps.net_io_counters(pernic=False)
        metrics.add_network_stats(
            net_counters.bytes_recv,
            net_counters.packets_recv,
            net_counters.bytes_sent,
            net_counters.packets_sent)

    @staticmethod
    def network_connections(metrics):
        protocols = ['tcp']
        for protocol in protocols:
            for c in ps.net_connections(kind=protocol):
                try:
                    if c.status == "ESTABLISHED" or c.status == "BOUND":
                        metrics.add_network_connection(c.raddr.ip, c.raddr.port,
                                                       Collector.__get_interface_name(c.laddr.ip),
                                                       c.laddr.port)
                except Exception as ex:
                    print('Failed to parse network info for protocol: ' + protocol)
                    print(ex)

    def add_custom_metrics(self, metrics, custom_metrics):
        self.cpu_usage(metrics, custom_metrics)
        self.ram_usage(metrics, custom_metrics)
        self.ram_swap_usage(metrics, custom_metrics)
        self.bandwidth_per_second_usage(metrics, custom_metrics)
        self.processes_count(metrics, custom_metrics)
        self.containers_count(metrics, custom_metrics)

    @staticmethod
    def cpu_usage(metrics, custom_metrics):
        # cpu_percent = ps.cpu_percent(interval=None)
        cpu_percent = custom_metrics.get("cpu_percent", 0)
        metrics.add_cpu_usage(cpu_percent)

    @staticmethod
    def ram_usage(metrics, custom_metrics):
        # cpu_percent = ps.cpu_percent(interval=None)
        ram_percent = custom_metrics.get("ram_percent", 0)
        metrics.add_ram_usage(ram_percent)

    @staticmethod
    def ram_swap_usage(metrics, custom_metrics):
        # cpu_percent = ps.cpu_percent(interval=None)
        ram_swap_percent = custom_metrics.get("ram_swap_percent", 0)
        metrics.add_ram_swap_usage(ram_swap_percent)

    @staticmethod
    def bandwidth_per_second_usage(metrics, custom_metrics):
        # cpu_percent = ps.cpu_percent(interval=None)
        bandwidth_per_second = custom_metrics.get("bandwidth_per_second", 0)
        metrics.add_bandwidth_per_second_usage(bandwidth_per_second)

    @staticmethod
    def processes_count(metrics, custom_metrics):
        # cpu_percent = ps.cpu_percent(interval=None)
        processes_count = custom_metrics.get("processes_count", 0)
        metrics.add_processes_count(processes_count)

    @staticmethod
    def containers_count(metrics, custom_metrics):
        # cpu_percent = ps.cpu_percent(interval=None)
        containers_count = custom_metrics.get("containers_count", 0)
        metrics.add_containers_count(containers_count)

    def collect_metrics(self, custom_metrics: dict):
        """Sample system metrics and populate a metrics object suitable for publishing to Device Defender."""
        metrics_current = metrics.Metrics(
            short_names=self._short_names, last_metric=self._last_metric)

        self.network_stats(metrics_current)
        self.listening_ports(metrics_current)
        self.network_connections(metrics_current)

        self.add_custom_metrics(metrics_current, custom_metrics)

        self._last_metric = metrics_current
        return metrics_current


def main():
    """Use this method to run the collector in stand-alone mode to tests metric collection."""
    collector = Collector(short_metrics_names=False)

    while True:
        # setup a loop to collect
        metric = collector.collect_metrics({})
        print(metric.to_json_string(pretty_print=True))

        sleep(1)


if __name__ == '__main__':
    main()
