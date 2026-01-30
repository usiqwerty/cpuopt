# * add status as one of the available options
# * alert user on snap if detected and how to remove first time live/stats message starts
# * if daemon is disabled and auto-cpufreq is removed (snap) remind user to enable it back
import subprocess
from argparse import ArgumentParser
from shutil import which
from sys import argv

# ToDo: update README part how to run this script
from cpuopt.core import *
from cpuopt.globals import GITHUB
from cpuopt.tlp_stat_parser import TLPStatusParser
from cpuopt.utils import root_check, app_name


def header(): print("\n------------------------- auto-cpufreq: Power helper -------------------------\n")


def warning(): print("\n----------------------------------- Warning -----------------------------------\n")


def helper_opts(): print("\nFor full list of options run: python3 -m auto_cpufreq.power_helper --help")


# used to check if binary exists on the system
def does_command_exists(cmd): return which(cmd) is not None


bluetoothctl_exists = does_command_exists("bluetoothctl")
powerprofilesctl_exists = does_command_exists("powerprofilesctl")
systemctl_exists = does_command_exists("systemctl")
tlp_stat_exists = does_command_exists("tlp-stat")
tuned_stat_exists = does_command_exists("tuned")

# detect if gnome power profile service is running
if systemctl_exists:
    try:
        gnome_power_status = subprocess.call(["systemctl", "is-active", "--quiet", "power-profiles-daemon"])
    except:
        print("\nUnable to determine init system")
        print("If this causes any problems, please submit an issue:")
        print(GITHUB + "/issues")


# alert in case TLP service is running
def tlp_service_detect():
    if tlp_stat_exists:
        status_output = subprocess.getoutput("tlp-stat -s")
        tlp_status = TLPStatusParser(status_output)
        if tlp_status.is_enabled():
            warning()
            print("Detected you are running a TLP service!")
            print("This daemon might interfere with auto-cpufreq which can lead to unexpected results.")
            print("We strongly encourage you to remove TLP unless you really know what you are doing.")


# alert in case gnome power profile service is running
def gnome_power_detect():
    if systemctl_exists and not bool(gnome_power_status):
        warning()
        print("Detected running GNOME Power Profiles daemon service!")
        print("\nThis daemon might interfere with auto-cpufreq and will be automatically")
        print("disabled when auto-cpufreq daemon is installed and")
        print("it will be re-enabled after auto-cpufreq is removed.")

        print("\nOnly necessary to be manually done on Snap package installs!")
        print("Steps to perform this action using auto-cpufreq: power_helper script:")
        print(f"git clone {GITHUB}.git")
        print("python3 -m auto_cpufreq.power_helper --gnome_power_disable")
        print(f"\nReference: {GITHUB}#configuring-auto-cpufreq")


# enable gnome >= 40 power profiles (uninstall)
def gnome_power_svc_enable():
    if systemctl_exists:
        try:
            print("* Enabling GNOME power profiles\n")
            subprocess.call(["systemctl", "unmask", "power-profiles-daemon"])
            subprocess.call(["systemctl", "enable", "--now", "power-profiles-daemon"])
        except:
            print("\nUnable to enable GNOME power profiles")
            print("If this causes any problems, please submit an issue:")
            print(GITHUB + "/issues")


# gnome power profiles current status
def gnome_power_svc_status():
    if systemctl_exists:
        try:
            print("* GNOME power profiles status")
            subprocess.call(["systemctl", "status", "power-profiles-daemon"])
        except:
            print("\nUnable to see GNOME power profiles status")
            print("If this causes any problems, please submit an issue:")
            print(GITHUB + "/issues")


# disable bluetooth on boot
def bluetooth_disable():
    if bluetoothctl_exists:
        print("* Turn off Bluetooth on boot (only)!")
        print("  If you want bluetooth enabled on boot run: auto-cpufreq --bluetooth_boot_on")
        btconf = Path("/etc/bluetooth/main.conf")
        try:
            orig_set = "AutoEnable=true"
            change_set = "AutoEnable=false"
            with btconf.open(mode="r+") as f:
                content = f.read()
                f.seek(0)
                f.truncate()
                f.write(content.replace(orig_set, change_set))
        except Exception as e:
            print(f"\nERROR:\nWas unable to turn off bluetooth on boot\n{repr(e)}")
    else:
        print("* Turn off bluetooth on boot [skipping] (package providing bluetooth access is not present)")


# enable bluetooth on boot
def bluetooth_enable():
    if bluetoothctl_exists:
        print("* Turn on bluetooth on boot")
        btconf = "/etc/bluetooth/main.conf"
        try:
            orig_set = "AutoEnable=true"
            change_set = "AutoEnable=false"
            with open(btconf, "r+") as f:
                content = f.read()
                f.seek(0)
                f.truncate()
                f.write(content.replace(change_set, orig_set))
        except Exception as e:
            print(f"\nERROR:\nWas unable to turn on bluetooth on boot\n{repr(e)}")
    else:
        print("* Turn on bluetooth on boot [skipping] (package providing bluetooth access is not present)")


def disable_power_profiles_daemon():
    # always disable power-profiles-daemon
    try:
        print("\n* Disabling GNOME power profiles")
        subprocess.call(["systemctl", "disable", "--now", "power-profiles-daemon"])
        subprocess.call(["systemctl", "mask", "power-profiles-daemon"])
    except:
        print("\nUnable to disable GNOME power profiles")
        print("If this causes any problems, please submit an issue:")
        print(GITHUB + "/issues")


# default gnome_power_svc_disable func (balanced)
def gnome_power_svc_disable():
    snap_pkg_check = 0
    if systemctl_exists:
        if bool(gnome_power_status):
            try:
                # check if snap package installed
                snap_pkg_check = subprocess.call(['snap', 'list', '|', 'grep', 'auto-cpufreq'],
                                                 stdout=subprocess.DEVNULL,
                                                 stderr=subprocess.STDOUT)
                # check if snapd is present and if snap package is installed | 0 is success
                if not bool(snap_pkg_check):
                    print("GNOME Power Profiles Daemon is already disabled, it can be re-enabled by running:\n"
                          "sudo python3 -m auto_cpufreq.power_helper --gnome_power_enable\n"
                          )
                elif snap_pkg_check == 1:
                    print(
                        "auto-cpufreq snap package not installed\nGNOME Power Profiles Daemon should be enabled. run:\n\n"
                        "sudo python3 -m auto_cpufreq.power_helper --gnome_power_enable"
                    )
            except:
                # snapd not found on the system
                print("There was a problem, couldn't determine GNOME Power Profiles Daemon")
                snap_pkg_check = 0

        if not bool(gnome_power_status) and powerprofilesctl_exists:
            if snap_pkg_check == 1:
                print(
                    "auto-cpufreq snap package not installed.\nGNOME Power Profiles Daemon should be enabled, run:\n\n"
                    "sudo python3 -m auto_cpufreq.power_helper --gnome_power_enable"
                )
            else:
                print("auto-cpufreq snap package installed, GNOME Power Profiles Daemon should be disabled.\n")
                print("Using profile: ", "balanced")
                subprocess.call(["powerprofilesctl", "set", "balanced"])

                disable_power_profiles_daemon()


# cli
argparser = ArgumentParser()

# @click.option("--gnome_power_disable", help="Disable GNOME Power profiles service (default: balanced), reference:\n https://bit.ly/3bjVZW1", type=click.Choice(['balanced', 'performance'], case_sensitive=False))
argparser.add_argument("--gnome_power_disable", action="store_true", help="Disable GNOME Power profiles service")
# ToDo:
# * update readme/docs
argparser.add_argument("--gnome_power_enable", action="store_true", help="Enable GNOME Power profiles service")

argparser.add_argument("--gnome_power_status", action="store_true", help="Get status of GNOME Power profiles service")
argparser.add_argument("--bluetooth_boot_on", action="store_true", help="Turn on Bluetooth on boot")
argparser.add_argument("--bluetooth_boot_off", action="store_true", help="Turn off Bluetooth on boot")


def main(
        gnome_power_enable,
        gnome_power_disable,
        gnome_power_status,
        bluetooth_boot_off,
        bluetooth_boot_on,
):
    root_check()
    header()

    if len(argv) == 1:
        print('Unrecognized option!\n\nRun: "' + app_name + ' --help" for list of available options.')
    else:
        if gnome_power_enable:
            gnome_power_svc_enable()
        elif gnome_power_disable:
            gnome_power_svc_disable()
        elif gnome_power_status:
            gnome_power_svc_status()
        elif bluetooth_boot_off:
            bluetooth_disable()
        elif bluetooth_boot_on:
            bluetooth_enable()
        helper_opts()


if __name__ == "__main__":
    args = argparser.parse_args()
    main(
        args.gnome_power_enable,
        args.gnome_power_disable,
        args.gnome_power_status,
        args.bluetooth_boot_off,
        args.bluetooth_boot_on,
    )
