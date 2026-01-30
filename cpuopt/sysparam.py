import os
from pathlib import Path
from subprocess import getoutput
from typing import Literal, NamedTuple

import psutil

from cpuopt.config import config
from cpuopt.cpufreqctl import get_frequency_max_limit, get_frequency_min_limit, \
    set_freq_max, set_freq_min
from cpuopt.globals import CPUS, POWER_SUPPLY_DIR

powersave_load_threshold = (75 * CPUS) / 100
performance_load_threshold = (50 * CPUS) / 100
governor_override = "default"

cpufreq_boost = Path("/sys/devices/system/cpu/cpufreq/boost")

cpu_intel_pstate = Path("/sys/devices/system/cpu/intel_pstate")
intel_pstate_status = Path("/sys/devices/system/cpu/intel_pstate/status")
intel_pstate_no_turbo = Path("/sys/devices/system/cpu/intel_pstate/no_turbo")
pstate_hwp_dynboost = Path("/sys/devices/system/cpu/intel_pstate/hwp_dynamic_boost")

amd_pstate = Path("/sys/devices/system/cpu/amd_pstate")
amd_pstate_status = Path("/sys/devices/system/cpu/amd_pstate/status")
acpi_platform_profile = Path("/sys/firmware/acpi/platform_profile")

cpu0_epp = Path("/sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference")
last_charge_status = None
prev_power_supply = None
phys_max_limit = get_frequency_max_limit()
phys_min_limit = get_frequency_min_limit()


class PowerSupply(NamedTuple):
    name: str
    path: Path
    online_value: str


def get_override():
    return governor_override


def get_turbo():
    print("Currently turbo boost is:", "on" if turbo() else "off")


def set_turbo(value: bool):
    turbo(value)


def get_load():
    cpuload = psutil.cpu_percent(interval=1)  # get CPU utilization as a percentage
    load1m, _, _ = os.getloadavg()  # get system/CPU load
    return cpuload, load1m


def display_system_load_avg():
    print(" (load average: {:.2f}, {:.2f}, {:.2f})".format(*os.getloadavg()))


def set_platform_profile(conf, profile):
    if not acpi_platform_profile.exists():
        pass
        # print('Not setting Platform Profile (not supported by system)')
    else:
        pp = conf[profile]["platform_profile"]
        acpi_platform_profile.write_text(str(pp))


def set_energy_perf_bias(conf, profile: Literal['battery', 'charger']):
    if cpu_intel_pstate.exists() is False:
        # print('Not setting EPB (not supported by system)')
        return
    epb = conf[profile]["energy_perf_bias"]
    epb_numeric = epb
    if epb == 'performance':
        epb_numeric = 0
    elif epb == 'balance_performance':
        epb_numeric = 4
    elif epb == 'default':
        epb_numeric = 6
    elif epb == 'balance_power':
        epb_numeric = 8
    elif epb == 'power':
        epb_numeric = 15

    for core in range(CPUS):
        epb_path = Path(f"/sys/devices/system/cpu/cpu{core}/power/energy_perf_bias")
        epb_path.write_text(str(epb_numeric))


def set_frequencies():
    """
    Sets frequencies:
     - if option is used in auto-cpufreq.conf: use configured value
     - if option is disabled/no conf file used: set default frequencies
    Frequency setting is performed only once on power supply change
    """
    global last_charge_status
    charging_status = charging()

    # don't do anything if the power supply hasn't changed
    # TODO: why so?
    if charging_status == last_charge_status:
        return
    else:
        last_charge_status = charging_status

    conf = config.get_config()

    power_supply = "charger" if charging_status else "battery"
    set_freq_max(int(conf[power_supply]["scaling_max_freq"]))
    set_freq_min(int(conf[power_supply]["scaling_min_freq"]))


def turbo(value: bool = None):
    """
    Get and set turbo mode
    """
    if intel_pstate_no_turbo.exists():
        inverse = True
        f = intel_pstate_no_turbo
    elif cpufreq_boost.exists():
        f = cpufreq_boost
        inverse = False
    elif amd_pstate_status.exists():
        amd_value = amd_pstate_status.read_text().strip()
        if amd_value == "active":
            print("CPU turbo is controlled by amd-pstate-epp driver")
        # Basically, no other value should exist.
        return False
    else:
        print("Warning: CPU turbo is not available")
        return False

    if value is not None:
        try:
            f.write_text(f"{int(value ^ inverse)}\n")
        except PermissionError:
            print("Warning: Changing CPU turbo is not supported. Skipping.")
            return False

    return bool(int(f.read_text().strip())) ^ inverse


def charging():
    global last_charge_status
    """
    get charge state: is battery charging or discharging
    """
    # check if we found power supplies. on a desktop these are not found and we assume we are on a powercable.
    if len(power_supplies) == 0:
        return True  # nothing found, so nothing to check
    for _, supply_file_path, charging_value in tracked_power_supplies:
        with open(supply_file_path) as f:
            charge_status = f.read()[:-1] == charging_value
            if charge_status != last_charge_status:
                print(f"Changing charging status to {charge_status}")
                last_charge_status = charge_status
            return charge_status

    return True  # we cannot determine discharging state, assume we are on powercable


def get_power_supply_ignore_list():
    conf = config.get_config()

    list = []

    if conf.has_section("power_supply_ignore_list"):
        for i in conf["power_supply_ignore_list"]:
            list.append(conf["power_supply_ignore_list"][i])

    # these are hard coded power supplies that will always be ignored
    list.append("hidpp_battery")
    return list


power_supplies = sorted(os.listdir(Path(POWER_SUPPLY_DIR)))
POWER_SUPPLY_IGNORELIST = get_power_supply_ignore_list()

tracked_power_supplies: list[PowerSupply] = []

# from the highest performance to the lowest
ALL_GOVERNORS = ('performance', 'ondemand', 'conservative', 'schedutil', 'userspace', 'powersave')
AVAILABLE_GOVERNORS = getoutput('cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors').strip().split(
    ' ')
AVAILABLE_GOVERNORS_SORTED = tuple(filter(lambda gov: gov in AVAILABLE_GOVERNORS, ALL_GOVERNORS))

for supply in power_supplies:
    # Check if supply is in ignore list, if found in ignore list, skip it.
    if any(item in supply for item in POWER_SUPPLY_IGNORELIST):
        continue
    power_supply_type_path = Path(POWER_SUPPLY_DIR + supply + "/type")
    if not power_supply_type_path.exists():
        continue
    with open(power_supply_type_path) as f:
        supply_type = f.read()[:-1]
    if supply_type == "Mains":
        # we found an AC
        power_supply_online_path = Path(POWER_SUPPLY_DIR + supply + "/online")
        if not power_supply_online_path.exists():
            continue
        tracked_power_supplies.append(PowerSupply(supply, power_supply_online_path, '1'))

    elif supply_type == "Battery":
        # we found a battery, check if its being discharged
        power_supply_status_path = Path(POWER_SUPPLY_DIR + supply + "/status")
        if not power_supply_status_path.exists():
            continue
        tracked_power_supplies.append(PowerSupply(supply, power_supply_status_path, 'Charging'))

print("Power supplies:", ', '.join([n for n, _, _ in tracked_power_supplies]))
