from src.models.hardware_telemetry.network import NetworkIoCounters, NetworkGeneralStats

network_io_counters_model = NetworkIoCounters()
network_io_counters_model.retrieve()
parsed_network_io_counters_model = network_io_counters_model.to_dict()

network_general_stats_model = NetworkGeneralStats()
network_general_stats_model.retrieve()
parsed_network_general_stats_model = network_general_stats_model.to_dict()

network_general_stats_model.background_functions_run()
