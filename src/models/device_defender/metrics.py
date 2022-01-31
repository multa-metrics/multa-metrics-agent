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

import time
import json
import cbor
import random
import os
import tags
from ipaddress import ip_address, IPv4Address


class Metrics(object):
    """Metrics

    A collection of system metric values, providing facilities for output in a Device Defender compliant format.

    Features:
        **Serialization Format**: Metrics can be exported in either `cbor <http://cbor.io/>`_ or JSON format.

        **Delta metrics**: if the class is initialized with a existing metrics object,
        for certain metrics, the difference between the old an current metric value will calculated and stored.

        **Selectable metric tags**: allow for verbose metrics tags, for easier debugging, or short memonic tags,
        reducing the amount data transmitted and stored in memory.

    """

    def __init__(self, short_names=False, last_metric=None):
        """Initialize a new metrics object.

        Parameters
        ----------
        short_names : bool
                Toggle short object tags in output metrics.
        last_metric : Metrics object
                Metric object used for delta metric calculation.
        """
        self.t = tags.Tags(short_names)
        # Header Information
        self._timestamp = int(time.time())
        if last_metric is None:
            self.interval = 0
        else:
            self.interval = self._timestamp - last_metric._timestamp

        # Network Metrics
        self._net_connections = []
        self.listening_tcp_ports = []
        self.listening_udp_ports = []

        # Custom Metrics
        self.cpu_metrics = []
        self.ram_metrics = []
        self.ram_swap_metrics = []
        self.bandwidth_per_second_metrics = []
        self.processes_count_metrics = []
        self.containers_count_metrics = []

        # Network Stats By Interface
        self.total_counts = {}  # The raw values from the system
        self._interface_stats = {}  # The diff values, if delta metrics are used
        if last_metric is None:
            self._old_interface_stats = {}
        else:
            self._old_interface_stats = last_metric.total_counts

        self.max_list_size = 50

    @property
    def network_stats(self):
        """Retrieve network TCP and UDP stats aggregated across all interfaces."""
        return self._interface_stats

    def listening_ports(self, protocol):
        if protocol.upper() == "UDP":
            return self.listening_udp_ports
        elif protocol.upper() == "TCP":
            return self.listening_tcp_ports
        else:
            print(("Invalid Protocol: " + protocol))
            return []

    def add_listening_ports(self, protocol, ports):
        """
        Add a sets of listening ports for a particular protocol.

        Parameters
        ----------
        protocol: string
          TCP or UDP, all others invalid and will not be added
        ports: list
           List of Dictionaries, each dictionary should have a "port" and optionally an "interface" key.
           Example Dictionary: {'port': 80, 'interface': 'eth0'}

        """
        if protocol.upper() == "UDP":
            for p in ports:
                if p not in self.listening_udp_ports:
                    self.listening_udp_ports += ports
        elif protocol.upper() == "TCP":
            for p in ports:
                if p not in self.listening_tcp_ports:
                    self.listening_tcp_ports += ports
        else:
            print(("Invalid Protocol: " + protocol))

    def add_network_stats(self, bytes_in, packets_in, bytes_out, packets_out):
        """
        Add cumulative network stats across all network interfaces.
        If a previous metrics object was supplied,attempts to calculate and store delta metric.

        Parameters
        ----------
        bytes_in: int
           Number of bytes received on this interface
        bytes_out: int
           Number of bytes sent from this interface
        packets_in: int
           Number of packets received on this interface
        packets_out: int
           Number of packets sent from this interface
        """
        self.total_counts = {
            'bytes_in': bytes_in,
            'bytes_out': bytes_out,
            'packets_in': packets_in,
            'packets_out': packets_out
        }

        if self._old_interface_stats:
            bytes_in_diff = bytes_in - self._old_interface_stats[self.t.bytes_in]
            bytes_out_diff = bytes_out - self._old_interface_stats[self.t.bytes_out]
            packets_in_diff = packets_in - self._old_interface_stats[self.t.packets_in]
            packets_out_diff = packets_out - self._old_interface_stats[self.t.packets_out]

            self._interface_stats = {self.t.bytes_in: bytes_in_diff,
                                     self.t.bytes_out: bytes_out_diff,
                                     self.t.packets_in: packets_in_diff,
                                     self.t.packets_out: packets_out_diff}

        else:
            self._interface_stats = {self.t.bytes_in: bytes_in, self.t.bytes_out: bytes_out,
                                     self.t.packets_in: packets_in,
                                     self.t.packets_out: packets_out}

    def add_network_connection(self, remote_addr, remote_port, interface, local_port):
        """
        Add network connection details.

        Parameters
        ----------
        remote_addr: string
            Ip address of the remote peer, can be ipv4 or ipv6
        remote_port: int
            Port of the remote peer
        interface: string
            Name of local network interface associated with the connection
        local_port: int
            Local port of the connection
        """
        ipAddress = remote_addr
        if type(ip_address(remote_addr)) is not IPv4Address:
            ipAddress = "[" + remote_addr + "]"
        new_conn = {self.t.remote_addr: ipAddress + ":" + str(remote_port),
                    self.t.local_interface: interface,
                    self.t.local_port: local_port}

        if new_conn not in self._net_connections:
            self._net_connections.append(new_conn)

    def add_cpu_usage(self, cpu_usage):
        """
        Add cpu usage details.

        Parameters
        ----------
        cpu_usage: float
             representing the current system-wide CPU utilization as a percentage
        """
        self.cpu_metrics = {"number": cpu_usage}

    def add_ram_usage(self, ram_usage):
        """
        Add ram usage details.

        Parameters
        ----------
        ram_usage: float
             representing the current system-wide RAM utilization as a percentage
        """
        self.ram_metrics = {"number": ram_usage}

    def add_ram_swap_usage(self, ram_swap_usage):
        """
        Add ram usage details.

        Parameters
        ----------
        ram_swap_usage: float
             representing the current system-wide RAM SWAP utilization as a percentage
        """
        self.ram_swap_metrics = {"number": ram_swap_usage}

    def add_bandwidth_per_second_usage(self, bandwidth_per_second_usage):
        """
        Add ram usage details.

        Parameters
        ----------
        bandwidth_per_second_usage: float
             representing the current system-wide Bandwidth per Second utilization as a percentage
        """
        self.bandwidth_per_second_metrics = {"number": bandwidth_per_second_usage}

    def add_processes_count(self, processes_count):
        """
        Add ram usage details.

        Parameters
        ----------
        processes_count: float
             representing the current system-wide processes count
        """
        self.processes_count_metrics = {"number": processes_count}

    def add_containers_count(self, containers_count):
        """
        Add ram usage details.

        Parameters
        ----------
        containers_count: float
             representing the current system-wide containers count
        """
        self.containers_count_metrics = {"number": containers_count}

    @property
    def network_connections(self):
        return self._net_connections

    def _sample_list(self, input_list):
        """
        Downsamples a list to a desired size, choosing random elements from input list.

        Parameters
        ----------
        input_list: list
           List of arbitrary size

        Returns
        -------
           A list of of length of less than or equal to max_list_size,
           with items randomly selected from input list

        """
        if self.max_list_size and len(input_list) > self.max_list_size:
            random.seed(os.urandom(50))
            output_list = random.sample(input_list, self.max_list_size)
            return output_list
        else:
            return input_list

    def to_json_string(self, pretty_print=False):
        """
        Convert the metrics to a json string suitable for AWS IoT Device Defender.

        Parameters
        ----------
        pretty_print: bool
            Set to true if you would like json to be formatted in a more human-friendly format.

        """
        metrics = self._v1_metrics()
        if pretty_print:
            return json.dumps(metrics, indent=4, sort_keys=True)
        else:
            return json.dumps(metrics, separators=(',', ':'))

    def to_cbor(self):
        """Returns a cbor serialized metrics object."""
        return cbor.dumps(self._v1_metrics())

    def _v1_metrics(self):
        """Format metrics in Device Defender version 1 format."""

        t = self.t
        header = {t.report_id: self._timestamp,
                  t.version: "1.0"}
        metrics = {}

        if self.network_stats:
            metrics[t.interface_stats] = self.network_stats

        if self._net_connections:
            metrics[t.tcp_conn] = {t.established_connections: {t.connections: self._sample_list(self._net_connections),
                                                               t.total: len(self._net_connections)}}

        if self.listening_tcp_ports:
            metrics[t.listening_tcp_ports] = {t.ports: self._sample_list(self.listening_tcp_ports),
                                              t.total: len(self.listening_tcp_ports)}

        if self.listening_udp_ports:
            metrics[t.listening_udp_ports] = {t.ports: self._sample_list(self.listening_udp_ports),
                                              t.total: len(self.listening_udp_ports)}

        report = {
            t.header: header,
            t.metrics: metrics,
        }

        report[t.custom_metrics] = {}

        if self.cpu_metrics:
            report[t.custom_metrics][t.cpu_usage] = [self.cpu_metrics]

        if self.ram_metrics:
            report[t.custom_metrics][t.ram_usage] = [self.ram_metrics]

        if self.ram_swap_metrics:
            report[t.custom_metrics][t.ram_swap_usage] = [self.ram_swap_metrics]

        if self.bandwidth_per_second_metrics:
            report[t.custom_metrics][t.bandwidth_per_second] = [self.bandwidth_per_second_metrics]

        if self.processes_count_metrics:
            report[t.custom_metrics][t.processes_count] = [self.processes_count_metrics]

        if self.containers_count_metrics:
            report[t.custom_metrics][t.containers_count] = [self.containers_count_metrics]

        return report