from configparser import ConfigParser

import psutil

from cpuopt.config import config
from cpuopt.cpufreqctl import set_scaling_governor, set_energy_performance_preference
from cpuopt.sysparam import get_override, cpu0_epp, cpu_intel_pstate, pstate_hwp_dynboost, intel_pstate_status, \
    amd_pstate_status, amd_pstate, set_platform_profile, set_energy_perf_bias, set_frequencies, get_load, set_turbo, \
    performance_load_threshold, AVAILABLE_GOVERNORS_SORTED
from cpuopt.modules.system_info import SystemInfo

def set_performance():
    conf = config.get_config()
    gov = conf["charger"]["governor"] if conf.has_option("charger", "governor") else AVAILABLE_GOVERNORS_SORTED[0]

    if get_override() != "default":
        print("Warning: governor overwritten using `--force` flag.")
    set_scaling_governor(gov)

    if not cpu0_epp.exists():
        # print('Not setting EPP (not supported by system)')
        pass
    else:
        if cpu_intel_pstate.exists():
            set_intel_pstate(conf, gov)
        elif amd_pstate.exists():
            set_amd_pstate(conf, gov)

    set_energy_perf_bias(conf, "charger")
    set_platform_profile(conf, "charger")
    set_frequencies()

    cpuload, load1m = get_load()
    auto = conf["charger"]["turbo"] if conf.has_option("charger", "turbo") else "auto"

    if auto == "always":
        print("Configuration file enforces turbo boost")
        set_turbo(True)
    elif auto == "never":
        print("Configuration file disables turbo boost")
        set_turbo(False)
    else:
        set_auto_turboboost(cpuload, load1m)


def set_auto_turboboost(cpuload, load1m):
    if (
            psutil.cpu_percent(percpu=False, interval=0.01) >= 20.0
            or max(psutil.cpu_percent(percpu=True, interval=0.01)) >= 75
    ):
        print("High CPU load", end="")

        if cpuload >= 20:
            set_turbo(True)  # high cpu usage trigger
        elif SystemInfo.avg_temp() >= 70:  # set turbo state based on average of all core temperatures
            print(f"Optimal total CPU usage: {cpuload}%, high average core temp: {SystemInfo.avg_temp()}°C")
            set_turbo(False)
        else:
            set_turbo(True)
    elif load1m >= performance_load_threshold:

        print("High system load", end="")
        if cpuload >= 20:
            set_turbo(True)  # high cpu usage trigger
        elif SystemInfo.avg_temp() >= 65:  # set turbo state based on average of all core temperatures
            print(f"Optimal total CPU usage: {cpuload}%, high average core temp: {SystemInfo.avg_temp()}°C")
            set_turbo(False)
        else:
            set_turbo(True)
    else:
        print("Load optimal", end="")
        if cpuload >= 20:
            set_turbo(True)  # high cpu usage trigger
        else:  # set turbo state based on average of all core temperatures
            set_turbo(False)


def set_amd_pstate(conf, gov):
    if conf.has_option("charger", "energy_performance_preference"):
        epp = conf["charger"]["energy_performance_preference"]

        if (amd_pstate_status.exists() and
                open(amd_pstate_status, 'r').read().strip() == "active" and
                epp != "performance" and
                gov == "performance"):
            print(f'Warning "{epp} EPP cannot be used in performance governor')
            print('Overriding EPP to "performance"')
            epp = "performance"

        set_energy_performance_preference(epp)
        print(f'Setting to use: "{epp}" EPP')
    else:
        if amd_pstate_status.exists() and open(amd_pstate_status, 'r').read().strip() == "active":
            set_energy_performance_preference("performance")
            print('Setting to use: "performance" EPP')
        else:
            set_energy_performance_preference("balance_performance")
            print('Setting to use: "balance_performance" EPP')


def set_intel_pstate(conf: ConfigParser, gov: str):
    dynboost_enabled = pstate_hwp_dynboost.exists()
    if dynboost_enabled:
        dynboost_enabled = bool(int(pstate_hwp_dynboost.read_text()))

    if dynboost_enabled:
        print('Not setting EPP (dynamic boosting is enabled)')
    else:
        if conf.has_option("charger", "energy_performance_preference"):
            epp = conf["charger"]["energy_performance_preference"]

            if (intel_pstate_status.exists() and
                    intel_pstate_status.read_text().strip() == "active" and
                    epp != "performance" and
                    gov == "performance"):
                print(f'Warning "{epp}" EPP cannot be used in performance governor')
                print('Overriding EPP to "performance"')
                epp = "performance"

            set_energy_performance_preference(epp)
            # print(f'Setting to use: "{epp}" EPP')
        else:
            if intel_pstate_status.exists() and intel_pstate_status.read_text().strip() == "active":
                set_energy_performance_preference("performance")
            else:
                set_energy_performance_preference("balance_performance")

