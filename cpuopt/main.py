import sys
import time
from argparse import ArgumentParser
from subprocess import run

from cpuopt.battery_scripts.battery import battery_setup
from cpuopt.config import find_config_file, config as conf
from cpuopt.core import not_running_daemon_check, set_override, set_autofreq
from cpuopt.power_helper import gnome_power_detect, \
    tlp_service_detect, bluetooth_disable, bluetooth_enable
from cpuopt.sysparam import get_override
from cpuopt.utils import root_check, distro_info, app_version

argparser = ArgumentParser()
argparser.add_argument("--daemon", action="store_true")
argparser.add_argument("--force",
                       help="Force use of either \"powersave\" or \"performance\" governors. Setting to \"reset\" will go back to normal mode")

argparser.add_argument("--config", help="Use config file at defined path", )

argparser.add_argument("--get-state", action="store_true")
argparser.add_argument("--bluetooth_boot_off", action="store_true", help="Turn off Bluetooth on boot")
argparser.add_argument("--bluetooth_boot_on", action="store_true", help="Turn on Bluetooth on boot")
argparser.add_argument("--version", action="store_true", help="Show currently installed version")


def cli():
    args = argparser.parse_args()
    main(
        args.daemon,
        args.force,
        args.config,
        args.get_state,
        args.bluetooth_boot_off,
        args.bluetooth_boot_on,
        args.version
    )


def main(daemon, force, config, get_state, bluetooth_boot_off, bluetooth_boot_on, version):
    # display info if config file is used
    config_path = find_config_file(config)
    conf.set_path(config_path)
    # set governor override unless None or invalid
    if force is not None:
        not_running_daemon_check()
        root_check()  # Calling root_check before set_override as it will require sudo access
        set_override(force)  # Calling set override, only if force has some values

    if daemon:
        run_daemon()
    elif get_state:
        not_running_daemon_check()
        override = get_override()
        print(override)
    elif bluetooth_boot_off:
        run_bt_boot_off()
    elif bluetooth_boot_on:
        run_bt_boot_on()
    elif version:
        distro_info()
        app_version()


def run_bt_boot_on():
    root_check()
    bluetooth_enable()


def run_bt_boot_off():
    root_check()
    bluetooth_disable()


def run_daemon():
    root_check()
    gnome_power_detect()
    tlp_service_detect()
    battery_setup()
    conf.notifier.start()
    while True:
        try:
            set_autofreq()
            time.sleep(3)
        except KeyboardInterrupt:
            break
    conf.notifier.stop()
