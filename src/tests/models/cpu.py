from src.models.hardware_telemetry.cpu import CpuMixedStats, CpuStats, CpuTimes


cpu_times_model = CpuTimes()
cpu_times_model.retrieve()
parsed_cpu_times_model = cpu_times_model.to_dict()

cpu_stats_model = CpuStats()
cpu_stats_model.retrieve()
parsed_cpu_stats_model = cpu_stats_model.to_dict()

cpu_mixed_stats_model = CpuMixedStats()
cpu_mixed_stats_model.retrieve()
parsed_cpu_mixed_stats_model = cpu_mixed_stats_model.to_dict()

print("End")
