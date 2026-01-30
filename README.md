# cpuopt
[![Linux Build](https://github.com/usiqwerty/cpuopt/actions/workflows/build-linux.yml/badge.svg?event=push)](https://github.com/AdnanHodzic/auto-cpufreq/actions/workflows/build-linux.yml)
[![Nix Flake](https://github.com/usiqwerty/cpuopt/actions/workflows/build-nix.yaml/badge.svg?event=push)](https://github.com/AdnanHodzic/auto-cpufreq/actions/workflows/build-nix.yaml)

Minimalistic auto-cpufreq mod

**following text was not reviewed since creation of this fork, so you may need to discover things for yourself. This is an experimental tools for now**

## Why do I need auto-cpufreq?

One of the problems with Linux today on laptops is that the CPU will run in an unoptimized manner which will negatively impact battery life. For example, the CPU may run using the "performance" governor with turbo boost enabled regardless of whether it's plugged into a power outlet or not.

These issues can be mitigated by using tools like [indicator-cpufreq](https://itsfoss.com/cpufreq-ubuntu/) or [cpufreq](https://github.com/konkor/cpufreq), but those still require manual action from your side which can be daunting and cumbersome.

Tools like [TLP](https://github.com/linrunner/TLP) (which I used for numerous years) can help extend battery life, but may also create their own set of problems, such as losing turbo boost.

Given all of the above, I needed a simple tool that would automatically make CPU frequency-related changes and save battery life, but let the Linux kernel do most of the heavy lifting. That's how auto-cpufreq was born.

Please note: auto-cpufreq aims to replace TLP in terms of functionality, so after you install auto-cpufreq _it's recommended to remove TLP_. Using both for the same functionality (i.e., to set CPU frequencies) will lead to unwanted results like overheating. Hence, only use [both tools in tandem](https://github.com/AdnanHodzic/auto-cpufreq/discussions/176) if you know what you're doing.

One tool/daemon that does not conflict with auto-cpufreq in any way, and is even recommended to have running alongside, is [thermald](https://wiki.debian.org/thermald).

#### Supported architectures and devices

Only devices with an Intel, AMD, or ARM CPU are supported. This tool was developed to improve performance and battery life on laptops, but running it on desktops/servers (to lower power consumption) should also be possible.

## Features

- CPU frequency scaling, governor, and [turbo boost](https://en.wikipedia.org/wiki/Intel_Turbo_Boost) management based on
  - Battery state
  - CPU usage (total & per core)
  - CPU temperature in combination with CPU utilization/load (to prevent overheating)
  - System load
- Automatic CPU & power optimization (temporary and persistent)
- Settings battery charging thresholds (limited support)

## Installing auto-cpufreq
### AUR package (Arch based distributions)

[![AUR package](https://repology.org/badge/version-for-repo/aur/auto-cpufreq.svg)](https://aur.archlinux.org/packages/auto-cpufreq)

The AUR [Release Package](https://aur.archlinux.org/packages/auto-cpufreq) is currently being maintained by [MusicalArtist12](https://github.com/MusicalArtist12), [liljaylj](https://github.com/liljaylj), and [parmjotsinghrobot](https://github.com/parmjotsinghrobot). 

**Notices**

- The [Git Package](https://aur.archlinux.org/packages/auto-cpufreq-git) is seperately maintained and was last updated on version 1.9.6. 
- The build process links to `/usr/share/` instead of `/usr/local/share/`
- The daemon installer provided does not work, instead start the daemon with 

``` 
# systemctl enable --now auto-cpufreq 
```
- The GNOME Power Profiles daemon is [automatically disabled by auto-cpufreq-installer](https://github.com/AdnanHodzic/auto-cpufreq#1-power_helperpy-script-snap-package-install-only) due to it's conflict with auto-cpufreq.service. However, this doesn't happen with AUR installs, which can lead to problems (e.g., [#463](https://github.com/AdnanHodzic/auto-cpufreq/issues/463)) if not masked manually.
  - Open a terminal and run `sudo systemctl mask power-profiles-daemon.service` (then `enable` and `start` the auto-cpufreq.service if you haven't already).
- The TuneD daemon(enabled by default with Fedora 41) is [automatically disabled by auto-cpufreq-installer](https://github.com/AdnanHodzic/auto-cpufreq#1-power_helperpy-script-snap-package-install-only) due to it's conflict with auto-cpufreq.service.

### Installation (development mode only)

- If you have `poetry` installed:
  ```bash
  git clone https://github.com/AdnanHodzic/auto-cpufreq.git
  cd auto-cpufreq
  poetry install
  poetry run auto-cpufreq --help
  ```

- Alternatively, we can use an editable pip install for development purposes:
  ```bash
  git clone https://github.com/AdnanHodzic/auto-cpufreq.git
  cd auto-cpufreq
  # set up virtual environment (details removed for brevity)
  pip3 install -e .
  auto-cpufreq
  ```
- Regularly run `poetry update` if you get any inconsistent lock file issues.

## Post-installation

After installation, `auto-cpufreq` is available as a binary. Refer to [auto-cpufreq modes and options](https://github.com/AdnanHodzic/auto-cpufreq#auto-cpufreq-modes-and-options) for detailed information on how to run and configure `auto-cpufreq`.

## Configuring auto-cpufreq

auto-cpufreq makes all decisions automatically based on various factors such as CPU usage, temperature, and system load. However, it's possible to perform additional configurations:

### 1: power_helper.py script (Snap package install **only**)

When installing auto-cpufreq via [auto-cpufreq-installer](#auto-cpufreq-installer), if it detects the [GNOME Power Profiles service](https://twitter.com/fooctrl/status/1467469508373884933) is running, it will automatically disable it. Otherwise, that daemon will cause conflicts and various other performance issues. 

However, when auto-cpufreq is installed as a Snap package it's running as part of a container with limited permissions, hence it's *highly recommended* to disable the GNOME Power Profiles daemon using the `power_helper.py` script.

**Please Note:**<br>
The [`power_helper.py`](https://github.com/AdnanHodzic/auto-cpufreq/blob/master/auto_cpufreq/power_helper.py) script is located within the auto-cpufreq repo at `auto_cpufreq/power_helper.py`. In order to access it, first clone
the repository:

`git clone https://github.com/AdnanHodzic/auto-cpufreq`

Make sure to have `psutil` & `pyinotify` Python library installed before next step:

If you're using Debian based distro install them by running:

`sudo apt install python3-psutil python3-pyinotify` 

or manually using pip, e.g: 

`sudo pip3 install psutil pyinotify --break-system-packages`

Then disable the GNOME Power Profiles daemon:

`sudo python3 -m auto_cpufreq.power_helper --gnome_power_disable`

for full list of options run --help, e.g:

`sudo python3 -m auto_cpufreq.power_helper --help`

### 2: `--force` governor override

By default, auto-cpufreq uses `balanced` mode which works best for many systems and situations.

However, you can override this behaviour by switching to `performance` or `powersave` mode manually. The `performance` mode results in higher default frequencies, but also higher energy use (battery consumption) and should only be used if maximum performance is needed. The `powersave` mode does the opposite and extends battery life to its maximum.

See [`--force` flag](#overriding-governor) for more info.

### 3: auto-cpufreq config file

You can configure separate profiles for the battery and power supply. These profiles will let you pick which governor to use, as well as how and when turbo boost is enabled. The possible values for turbo boost behavior are `always`, `auto`, and `never`. The default behavior is `auto`, which only activates turbo during high load.

By default, auto-cpufreq does not use a config file. If you wish to configure auto-cpufreq statically, we look for a configuration file in the following order:

1. Commandline argument: `--config <FILE>` if passed as commandline argument to `auto-cpufreq`
2. User-specific configuration: `$XDG_CONFIG_HOME/auto-cpufreq/auto-cpufreq.conf`
3. System-wide configuration: `/etc/auto-cpufreq.conf`

#### Example config file contents
```python
# settings for when connected to a power source
[charger]
# see available governors by running: cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
# preferred governor
governor = performance

# EPP: see available preferences by running: cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_available_preferences
energy_performance_preference = performance

# EPB (Energy Performance Bias) for the intel_pstate driver
# see conversion info: https://www.kernel.org/doc/html/latest/admin-guide/pm/intel_epb.html
# available EPB options include a numeric value between 0-15
# (where 0 = maximum performance and 15 = maximum power saving),
# or one of the following strings:
# performance (0), balance_performance (4), default (6), balance_power (8), or power (15)
# if the parameter is missing in the config and the hardware supports this setting, the default value will be used
# the default value is `balance_performance` (for charger)
# energy_perf_bias = balance_performance

# Platform Profiles
# https://www.kernel.org/doc/html/latest/userspace-api/sysfs-platform_profile.html
# See available options by running:
# cat /sys/firmware/acpi/platform_profile_choices
# platform_profile = performance

# minimum cpu frequency (in kHz)
# example: for 800 MHz = 800000 kHz --> scaling_min_freq = 800000
# see conversion info: https://www.rapidtables.com/convert/frequency/mhz-to-hz.html
# to use this feature, uncomment the following line and set the value accordingly
# scaling_min_freq = 800000

# maximum cpu frequency (in kHz)
# example: for 1GHz = 1000 MHz = 1000000 kHz -> scaling_max_freq = 1000000
# see conversion info: https://www.rapidtables.com/convert/frequency/mhz-to-hz.html
# to use this feature, uncomment the following line and set the value accordingly
# scaling_max_freq = 1000000

# turbo boost setting. possible values: always, auto, never
turbo = auto

# settings for when using battery power
[battery]
# see available governors by running: cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors
# preferred governor
governor = powersave

# EPP: see available preferences by running: cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_available_preferences
energy_performance_preference = power

# EPB (Energy Performance Bias) for the intel_pstate driver
# see conversion info: https://www.kernel.org/doc/html/latest/admin-guide/pm/intel_epb.html
# available EPB options include a numeric value between 0-15
# (where 0 = maximum performance and 15 = maximum power saving),
# or one of the following strings:
# performance (0), balance_performance (4), default (6), balance_power (8), or power (15)
# if the parameter is missing in the config and the hardware supports this setting, the default value will be used
# the default value is `balance_power` (for battery)
# energy_perf_bias = balance_power

# Platform Profiles
# https://www.kernel.org/doc/html/latest/userspace-api/sysfs-platform_profile.html
# See available options by running:
# cat /sys/firmware/acpi/platform_profile_choices
# platform_profile = low-power

# minimum cpu frequency (in kHz)
# example: for 800 MHz = 800000 kHz --> scaling_min_freq = 800000
# see conversion info: https://www.rapidtables.com/convert/frequency/mhz-to-hz.html
# to use this feature, uncomment the following line and set the value accordingly
# scaling_min_freq = 800000

# maximum cpu frequency (in kHz)
# see conversion info: https://www.rapidtables.com/convert/frequency/mhz-to-hz.html
# example: for 1GHz = 1000 MHz = 1000000 kHz -> scaling_max_freq = 1000000
# to use this feature, uncomment the following line and set the value accordingly
# scaling_max_freq = 1000000

# turbo boost setting (always, auto, or never)
turbo = auto

# battery charging threshold
# reference: https://github.com/AdnanHodzic/auto-cpufreq/#battery-charging-thresholds
#enable_thresholds = true
#start_threshold = 20
#stop_threshold = 80
```

## How to run auto-cpufreq
auto-cpufreq should be run with with one of the following options:

- [monitor](#monitor)
  - Monitor and see suggestions for CPU optimizations

- [live](#live)
  - Monitor and automatically make (temporary) CPU optimizations

- [install](#install---auto-cpufreq-daemon) / [remove](#remove---auto-cpufreq-daemon)
  - Install/remove daemon for (permanent) automatic CPU optimizations
 
- [install (GUI)](#install---auto-cpufreq-daemon)
  - Install daemon via GUI for (permanent) automatic CPU optimizations

- [update](#update---auto-cpufreq-update)
  - Update auto-cpufreq to the latest release

- [install_performance](#1-power_helperpy-script)
  - Install daemon in "performance" mode

- [stats](#stats)
  - View live stats of CPU optimizations made by daemon

- [bluetooth_boot_off](#bluetooth_boot_off)
  - Turn off Bluetooth on boot (only)! Can be turned on any time later on.

- [bluetooth_boot_on](#bluetooth_boot_on)
  - Turn on Bluetooth on boot.

- [force=TEXT](#overriding-governor)
  - Force use of either the "powersave" or "performance" governor, or set to "reset" to go back to normal mode

- config=TEXT
  - Use config file at designated path

- debug
  - Show debug info (include when submitting bugs)

- version
  - Show currently installed version

- [donate](#financial-donation)
  - To support the project

- help
  - Shows all of the above options

- completions=TEXT
  - To support shell completions (current options are "bash", "zsh", or "fish")

Running `auto-cpufreq --help` will print the same list of options as above. Read [auto-cpufreq modes and options](#auto-cpufreq-modes-and-options) for more details.

## auto-cpufreq modes and options

### Monitor

`sudo auto-cpufreq --monitor`

No changes are made to the system. This is solely to demonstrate what auto-cpufreq could do for your system.

### Live

`sudo auto-cpufreq --live`

Necessary changes are temporarily made to the system over time, but this process and its changes are lost at system reboot. This mode is provided to evaluate how the system would behave with auto-cpufreq permanently running on the system.

### Overriding governor

`sudo auto-cpufreq --force=governor`

Force use of either the "powersave" or "performance" governor, or set to "reset" to go back to normal mode.
Please note that any set override will persist even after reboot.

### Install - auto-cpufreq daemon

Necessary changes are made to the system over time and this process will continue across reboots. The daemon is deployed and started as a systemd service. Changes are made automatically and live stats are generated for monitoring purposes.

**Install the daemon using CLI ([after installing auto-cpufreq](#installing-auto-cpufreq)):**

Installing the auto-cpufreq daemon using CLI is as simple as running the following command:

`sudo auto-cpufreq --install`

After the daemon is installed, `auto-cpufreq` is available as a binary and runs in the background. Its stats can be viewed by running: `auto-cpufreq --stats`

*Please note:* if the daemon is installed within a desktop environment, then its stats and options can be accessed via CLI or GUI. See "Install the daemon using GUI" below for more details.

**Install the daemon using GUI**

Starting with >= v2.0 [after installing auto-cpufreq](#installing-auto-cpufreq), an auto-cpufreq desktop entry (icon) is available, i.e.:

<img src="https://github.com/user-attachments/assets/f426d62b-00b0-4fa5-a72e-b352016ed448" width="640" alt="Example of auto-cpufreq desktop entry (icon)"/>

After selecting it to open the GUI, the auto-cpufreq daemon can be installed by clicking the "Install" button:

<img src="https://github.com/user-attachments/assets/5af47e5e-8b9e-4ff6-9ffc-e78acb623ce4" width="480" alt="The auto-cpufreq GUI's 'Install' button"/>

After that, the full auto-cpufreq GUI is available:

<img src="https://github.com/user-attachments/assets/9c7715c4-16b7-4a5c-86be-4c390276d9e8" width="640" alt="The full auto-cpufreq GUI"/>

*Please note:* after the daemon is installed (by any method), its stats and options are accessible via both CLI and GUI.

**auto-cpufreq daemon service**

Installing the auto-cpufreq daemon also enables the associated service (equivalent to `systemctl enable auto-cpufreq`), causing it to start on boot, and immediately starts it (equivalent to `systemctl start auto-cpufreq`).

Since the daemon is running as a systemd service, its status can be seen by running:

`systemctl status auto-cpufreq`

If installed via Snap package, daemon status can be viewed as follows:

`systemctl status snap.auto-cpufreq.service.service`

### Update - auto-cpufreq update

Update functionality works by cloning the auto-cpufreq repo, installing it via [auto-cpufreq-installer](#auto-cpufreq-installer), and performing a fresh [auto-cpufreq daemon install](#install---auto-cpufreq-daemon) to provide the [latest version's](https://github.com/AdnanHodzic/auto-cpufreq/releases) changes.

Update auto-cpufreq by running: `sudo auto-cpufreq --update`. By default, the latest revision is cloned to `/opt/auto-cpufreq/source`, thus maintaining existing directory structure.

Update and clone to a custom directory by running: `sudo auto-cpufreq --update=/path/to/directory`

### Remove - auto-cpufreq daemon

The auto-cpufreq daemon, its systemd service, and all its persistent changes can be removed by running:

`sudo auto-cpufreq --remove`

This does, in part, the equivalent of `systemctl stop auto-cpufreq && systemctl disable auto-cpufreq`, but the above command should be used instead of using `systemctl`.

*Please note:* after the daemon is removed, the auto-cpufreq GUI and desktop entry (icon) are also removed.

### Stats

If the daemon has been installed, live stats of CPU/system load monitoring and optimization can be seen by running:

`auto-cpufreq --stats`

### bluetooth_boot_off

Turn off Bluetooth on boot (only)! Bluetooth can still be turned on manually when needed. This option is executed during the installation of the auto-cpufreq daemon, but it can also be run independently without installing the daemon.

It prevents GNOME from automatically enabling Bluetooth on every reboot or after suspend/wake up even if you manually disable it, GNOME will turn it back on unless this option is used.

### bluetooth_boot_on

Useful if you prefer Bluetooth to be enabled at boot time, especially after installing the auto-cpufreq daemon, which will disable it by default.

## Battery charging thresholds

***Please note:** [Original implementor](https://github.com/AdnanHodzic/auto-cpufreq/pull/637) is looking for user input & testing to further improve this functionality. If you would like to help in this process, please refer to [Looking for developers and co-maintainers](https://github.com/AdnanHodzic/auto-cpufreq/#looking-for-developers-and-co-maintainers)*.

As of [v2.2.0](https://github.com/AdnanHodzic/auto-cpufreq/releases/tag/v2.2.0), battery charging thresholds can be set in the config file. This enforces your battery to start and stop charging at defined values.

### Supported devices

- **Lenovo ThinkPad** (thinkpad_acpi)*
- **Lenovo IdeaPad** (ideapad_acpi)*

***Please note, your laptop must have an installed ACPI kernel driver specific to the manufacturer.** To check if you have the correct module installed and loaded run `lsmod [module]`

**To request that your device be supported, please open an [issue](https://github.com/AdnanHodzic/auto-cpufreq/issues/new). In your issue, make us aware of the driver that works with your laptop**

### Battery config
Edit the config at `/etc/auto-cpufreq.conf`

Example config for battery ([already part of example config file](https://github.com/AdnanHodzic/auto-cpufreq/#example-config-file-contents))
```
[battery]
enable_thresholds = true
start_threshold = 20
stop_threshold = 80
```

### Lenovo_laptop conservation mode

this works only with `lenovo_laptop` kernel module compatable laptops.  

add `ideapad_laptop_conservation_mode = true` to your `auto-cpufreq.conf` file

### Special cases of Lenovo_ideapad (or some other models with fixed threshold)

As you may know, for some laptop models you can only decide to limit battery charging but can not set the limit value. The limit value is set by the manufacturer in the system (generally 60% and sometimes 80%). Also, you can not set the value of start charging.

This limit value is not always accessible for users to avoid changing it, but you can try looking in some of these paths : 

```
cat /sys/bus/platform/drivers/ideapad_acpi/VPC2004:00/charge_control_end_threshold
cat /sys/class/power_supply/BAT0/charge_control_end_threshold
cat /sys/class/power_supply/BAT0/charge_control_start_threshold
```

This is the config to apply at /etc/auto-cpufreq.conf in order to stop battery charging at 60% or 80% depending on the value set in the system by the manufacturer.

```
[battery]
enable_thresholds = true
start_threshold = 20
stop_threshold = 1

```
start_threshold = 20 (should be present with a valid number but it's ignored)

stop_threshold = 1 (to stop charging the battery at the limit value 60% or 80%)

### Ignoring power supplies

you may have a controler or headphones and when ever they may be on battery they might cause auto-cpufreq
to limit preformence to ignore them add to you config file the name of the power supply, under `[power_supply_ignore_list]`

the name of the power supply can be found with  `ls /sys/class/power_supply/`

```
[power_supply_ignore_list]

name1 = this
name2 = is 
name3 = an
name4 = example

# like this
xboxctrl = {the xbox controler power supply name}

```

## Troubleshooting

**Q:** If after installing auto-cpufreq you're (still) experiencing:
- high CPU temperatures
- CPU not scaling to minimum/maximum frequencies
- suboptimal CPU performance
- turbo mode not available

**A:** If you're using the `intel_pstate/amd-pstate` CPU management driver, consider changing it to `acpi-cpufreq`.

This can be done by editing the `GRUB_CMDLINE_LINUX_DEFAULT` params in `/etc/default/grub`. For instance:

```
    sudo nano /etc/default/grub
    # make sure you have nano installed, or you can use your favorite text editor
```

For Intel users:

```
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash intel_pstate=disable"
```

For AMD users:

```
GRUB_CMDLINE_LINUX_DEFAULT="quiet splash initcall_blacklist=amd_pstate_init amd_pstate.enable=0"
```

Once you have made the necessary changes to the GRUB configuration file, you can update GRUB by running `sudo update-grub` on Debian/Ubuntu, `sudo grub-mkconfig -o /boot/grub/grub.cfg` on Arch Linux, or one of the following on Fedora:

```
    sudo grub2-mkconfig -o /etc/grub2.cfg
```

```
    sudo grub2-mkconfig -o /etc/grub2-efi.cfg
```

```
    sudo grub2-mkconfig -o /boot/grub2/grub.cfg
    # legacy boot method
```

For systemd-boot users:

```
    sudo nano /etc/kernel/cmdline
    # make sure you have nano installed, or you can use your favorite text editor
```

For Intel users:

```
quiet splash intel_pstate=disable
```

For AMD users:

```
quiet splash initcall_blacklist=amd_pstate_init amd_pstate.enable=0
```

Once you have made the necessary changes to the `cmdline` file, you can update it by running `sudo reinstall-kernels`.

### AUR

- If the AUR installer does not work for your system, fallback to `auto-cpufreq-installer` and open an issue. 
