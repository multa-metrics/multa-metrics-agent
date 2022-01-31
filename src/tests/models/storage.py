from src.models.hardware_telemetry.storage import DiskGeneralStats, DiskIoCounters


disk_general_stats_model = DiskGeneralStats()
disk_general_stats_model.retrieve()
parsed_disk_general_stats_model = disk_general_stats_model.to_dict()

disk_io_counters_model = DiskIoCounters()
disk_io_counters_model.retrieve()
parsed_disk_io_counters_model = disk_io_counters_model.to_dict()

print("End")