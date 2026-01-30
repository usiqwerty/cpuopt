from cpuopt.config import config
from cpuopt.cpufreqctl import set_energy_performance_preference, set_scaling_governor
from cpuopt.sysparam import get_override, set_turbo, get_load, \
    set_platform_profile, set_energy_perf_bias, set_frequencies, pstate_hwp_dynboost, cpu0_epp


def set_powersave():
    conf = config.get_config()
    gov = conf["battery"]["governor"]

    if get_override() != "default":
        print("Warning: governor overwritten using `--force` flag.")
    set_scaling_governor(gov)

    if cpu0_epp.exists() is False:
        pass
        # print('Not setting EPP (not supported by system)')
    else:
        dynboost_enabled = pstate_hwp_dynboost.exists()
        if dynboost_enabled:
            dynboost_enabled = bool(int(pstate_hwp_dynboost.read_text()))

        if dynboost_enabled:
            print('Not setting EPP (dynamic boosting is enabled)')
        else:
            epp = conf["battery"]["energy_performance_preference"]
            set_energy_performance_preference(epp)
    set_energy_perf_bias(conf, "battery")
    set_platform_profile(conf, "battery")
    set_frequencies()

    cpuload, load1m = get_load()
    turbo = conf["battery"]["turbo"]

    if turbo == "always":
        print("Configuration file enforces turbo boost")
        set_turbo(True)
    elif turbo == "never":
        print("Configuration file disables turbo boost")
        set_turbo(False)
    else:
        if cpuload >= 20:
            set_turbo(True)  # high cpu usage trigger
        else:  # set turbo state based on average of all core temperatures
            set_turbo(False)
