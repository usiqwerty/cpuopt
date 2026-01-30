#!/usr/bin/env python3
#
# auto-cpufreq - core functionality
import json
import os
from pathlib import Path
from typing import Literal
from warnings import filterwarnings

from cpuopt.modes.performance import set_performance
from cpuopt.modes.powersave import set_powersave
from cpuopt.sysparam import get_override, charging
from cpuopt.utils import is_running

filterwarnings("ignore")

# add path to auto-cpufreq executables for GUI
if "PATH" in os.environ:
    os.environ["PATH"] += os.pathsep + "/usr/local/bin"
else:
    os.environ["PATH"] = "/usr/local/bin"


# ToDo:
# - replace get system/CPU load from: psutil.getloadavg() | available in 5.6.2)


# Note:
# "load1m" & "cpuload" can't be global vars and to in order to show correct data must be
# decraled where their execution takes place

# powersave/performance system load thresholds

# auto-cpufreq stats file path


# track governor override
governor_override_state = Path("/opt/auto-cpufreq/override.pickle")

if os.path.isfile(governor_override_state):
    with open(governor_override_state, "rb") as store:
        governor_override = json.load(store)
else:
    pass


def set_override(override: Literal["performance", "powersave", "reset"]):
    if override in ["powersave", "performance"]:
        with open(governor_override_state, "wb") as store:
            json.dump(override, store)
        print(f"Set governor override to {override}")
    elif override == "reset":
        if os.path.isfile(governor_override_state):
            os.remove(governor_override_state)
        print("Governor override removed")
    elif override is not None:
        print("Invalid option.\nUse force=performance, force=powersave, or force=reset")


def set_autofreq():
    """
    set cpufreq governor based on whether device is charging
    """
    override = get_override()
    if override == "powersave":
        set_powersave()
    elif override == "performance":
        set_performance()
    elif charging():
        set_performance()
    else:
        set_powersave()


def daemon_not_running_msg():
    print("\n" + "-" * 24 + " auto-cpufreq not running " + "-" * 30 + "\n")
    print(
        "ERROR: auto-cpufreq is not running in daemon mode.\n\nMake sure to run \"sudo auto-cpufreq --install\" first"
    )


# check if auto-cpufreq --daemon is not running
def not_running_daemon_check():
    if not is_running("auto-cpufreq", "--daemon"):
        daemon_not_running_msg()
        exit(1)

