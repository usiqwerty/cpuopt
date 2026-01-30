import os
import platform
from importlib.metadata import metadata, PackageNotFoundError
from os import path
from subprocess import getoutput
from sys import argv

import distro
import psutil


# display running version of auto-cpufreq
def app_version():
    print("auto-cpufreq version: ", end="")

    if IS_INSTALLED_WITH_AUR:
        print(getoutput("pacman -Qi auto-cpufreq | grep Version"))
    else:
        try:
            print(get_formatted_version())
        except Exception as e:
            print(repr(e))


def get_literal_version(package_name):
    try:
        package_metadata = metadata(package_name)
        package_name = package_metadata['Name']
        numbered_version, _, git_version = package_metadata['Version'].partition("+")

        return f"{numbered_version}+{git_version}"  # Construct the literal version string

    except PackageNotFoundError:
        return f"Package '{package_name}' not found"


def root_check():
    if not os.geteuid() == 0:
        print("\n" + "-" * 33 + " Root check " + "-" * 34 + "\n")
        print("ERROR:\n\nMust be run root for this functionality to work, i.e: \nsudo " + app_name)
        exit(1)


def distro_info():
    fdist = distro.linux_distribution()
    dist = " ".join(x for x in fdist)

    print("Linux distro: " + dist)
    print("Linux kernel: " + platform.release())


# return formatted version for a better readability
def get_formatted_version():
    splitted_version = get_literal_version("auto-cpufreq").split("+")
    return splitted_version[0] + ("" if len(splitted_version) > 1 else " (git: " + splitted_version[1] + ")")


# app_name var
app_name = "python3 power_helper.py" if argv[0] == "power_helper.py" else "auto-cpufreq"


# check if program (argument) is running

def is_running(program, argument):
    # iterate over all processes found by psutil
    # and find the one with name and args passed to the function
    for p in psutil.process_iter():
        try:
            cmd = p.cmdline()
        except:
            continue
        for s in filter(lambda x: program in x, cmd):
            if argument in cmd:
                return True


IS_INSTALLED_WITH_AUR = path.isfile("/etc/arch-release") and bool(getoutput("pacman -Qs auto-cpufreq"))
