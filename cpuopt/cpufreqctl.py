from pathlib import Path
from typing import Literal

from cpuopt.globals import CPUS


def set_energy_performance_preference(
        value: Literal["default", "performance", "balance_performance", "balance_power", "power"]):
    for core in range(CPUS):
        epp_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/energy_performance_preference")
        epp_path.write_text(value)


def set_scaling_governor(governor: str):
    for core in range(CPUS):
        sc_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_governor")
        sc_path.write_text(governor)


def get_frequency_max_limit(core: int = 0):
    max_freq_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/cpuinfo_max_freq")
    return int(max_freq_path.read_text())


def get_frequency_min_limit(core: int = 0):
    min_freq_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/cpuinfo_min_freq")
    return int(min_freq_path.read_text())


def get_freq_max(core: int = 0):
    freq_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_max_freq")
    return int(freq_path.read_text())


def set_freq_max(freq: int):
    for core in range(CPUS):
        freq_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_max_freq")
        freq_path.write_text(str(freq))


def get_freq_min(core: int = 0):
    freq_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_min_freq")
    return int(freq_path.read_text())


def set_freq_min(freq: int):
    for core in range(CPUS):
        freq_path = Path(f"/sys/devices/system/cpu/cpu{core}/cpufreq/scaling_min_freq")
        freq_path.write_text(str(freq))
