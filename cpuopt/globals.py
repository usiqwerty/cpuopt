import os

GITHUB = "https://github.com/AdnanHodzic/auto-cpufreq"
POWER_SUPPLY_DIR = "/sys/class/power_supply/"

CPU_TEMP_SENSOR_PRIORITY = ("coretemp", "acpitz", "k10temp", "zenpower")
CPUS = os.cpu_count()
