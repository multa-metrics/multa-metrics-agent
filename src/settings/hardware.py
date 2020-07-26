import os


RAM_THRESHOLD = int(os.environ.get("RAM_THRESHOLD", "80"))
CPU_THRESHOLD = int(os.environ.get("CPU_THRESHOLD", "80"))
CPU_ANALYSIS_TIME = int(os.environ.get("CPU_ANALYSIS_TIME", "5"))

HDD_THRESHOLD = int(os.environ.get("HDD_THRESHOLD", "80"))
TEMPERATURE_THRESHOLD = int(os.environ.get("TEMPERATURE_THRESHOLD", "80"))
BOOT_THRESHOLD = int(os.environ.get("BOOT_THRESHOLD", "7"))
UPTIME_THRESHOLD = int(os.environ.get("UPTIME_THRESHOLD", "20"))
BATTERY_THRESHOLD = int(os.environ.get("BATTERY_THRESHOLD", "15"))
