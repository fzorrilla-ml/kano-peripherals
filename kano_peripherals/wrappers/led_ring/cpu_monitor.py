# cpu_monitor.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# CPU Monitor animation that runs on either the Pi Hat or the LED Speaker.
#
# It works by polling the system and grabbing the top 10 most CPU intensive
# processes and mapping their respective PIDs onto LED ranges, e.g. PIDs
# between 1 - 1000 to LED 1, 1001 - 2000 to LED 2 and so on. The CPU load
# is added when mapped to each LED and is directly proportional to the
# blicking speed on the LED.


import sys
import math
import time
import dbus.exceptions
import traceback

from kano_settings.config_file import get_setting
from kano.utils import run_cmd
from kano.logging import logger

from kano_peripherals.wrappers.led_ring.base_animation import BaseAnimation
from kano_peripherals.return_codes import RC_FAILED_CPU_MONIT_FETCH, \
    RC_FAILED_ANIM_GET_DBUS, RC_FAILED_LOCKING_API


class CpuMonitor(BaseAnimation):
    """
    The OS cpu-monitor animation for an LED ring board.
    This is a wrapper over Pi Hat and LED Speaker.
    """

    LOCK_PRIORITY = 1
    RECONNECT_RETRY_TIME = 5  # seconds

    def __init__(self):
        super(CpuMonitor, self).__init__()

    def _reconnect(self):
        """ """
        while not self.connect(retry_count=0) and not self.interrupted:
            time.sleep(self.RECONNECT_RETRY_TIME)

        if self.interrupted:
            return False

        return True

    def start(self, update_rate, check_settings, retry_count):
        """
        Start the animation loop.

        Args:
            update_rate - int polling rate (sec) of cpu load and led index updating
            check_settings - bool whether to check kano-settings preference
            retry_count - int number of retries to grab DBus interface

        Returns:
            rc - int value with return code or None if no errors occured
        """

        # Check user preference about enabling the animation.
        if check_settings:
            cpu_monitor_on = self._get_cpu_monitor_setting()
            if not cpu_monitor_on:
                return

        # Connect to the DBus interface of a board with an LED ring.
        if not self._reconnect():
            logger.error('LED Ring: CpuMonitor: Could not aquire dbus interface!')
            return RC_FAILED_ANIM_GET_DBUS

        try:
            # Lock the API so anything below doesn't override our calls.
            locked = self.iface.lock(self.LOCK_PRIORITY)
            if not locked:
                logger.error('LED Ring: CpuMonitor: Could not lock dbus interface!')
                return RC_FAILED_LOCKING_API

            # Setup the animation parameters.
            num_leds = self.iface.get_num_leds()
            vf = self.constant([self.colours.LED_KANO_ORANGE for i in range(num_leds)])
            duration = update_rate
            cycles = duration / 2

            # Run the animation loop
            while not self.interrupted:
                led_speeds = self._get_cpu_led_speeds(0.1, num_leds)

                vf2 = self.pulse_each(vf, led_speeds)
                successful = self.animate(vf2, duration, cycles)

                if not successful:
                    time.sleep(duration)

        # Handle board hotplugging. The iface will not be able to reach the service it
        # connected to after the board was unplugged. We try to reconnect to the DBus
        # service here and restart the animation loop.
        except dbus.exceptions.DBusException:
            return self.start(update_rate, check_settings, retry_count)

        except Exception:
            logger.error(
                'CpuMonitor: start: Unexpected error occured:\n{}'
                .format(traceback.format_exc())
            )

        # The API will be unlocked in the signal handler routine.

    @staticmethod
    def stop():
        """
        Stop the animation loop and terminate process.
        """
        super(CpuMonitor, CpuMonitor).stop('cpu-monitor')

    def _get_cpu_monitor_setting(self):
        return get_setting('LED-Speaker-anim')

    def _get_cpu_led_speeds(self, speed_scale, num_leds):
        # get the top NUM_LEDS processes by CPU usage - PID, %CPU
        cmd = 'ps -eo pid,pcpu --no-headers --sort -pcpu | head -n {}'.format(num_leds)
        output, error, _ = run_cmd(cmd)

        if error:
            logger.error('_get_cpu_led_speeds: cmd error - [{}]'.format(error))
            sys.exit(RC_FAILED_CPU_MONIT_FETCH)

        try:
            pid_cpu_list = list()

            min_pid = sys.maxint
            max_pid = -sys.maxint - 1

            for line in output.strip().split('\n'):
                parts = line.split()
                pid = int(parts[0])
                cpu = float(parts[1])

                min_pid = min(pid, min_pid)
                max_pid = max(pid, max_pid)

                pid_cpu_list.append([pid, cpu])

            leds = [0 for i in range(num_leds)]
            step = (max_pid + min_pid) / float(num_leds)

            for pid_cpu in pid_cpu_list:
                # calculate the led_index based on the proc PID
                led_index = int(pid_cpu[0] / step)
                # adding the CPU load for multiple PIDs mapped to the same LED
                leds[led_index] += pid_cpu[1] * speed_scale
                # capping the LED speed to 100% CPU load (can be >100%, multicore)
                leds[led_index] = min(math.ceil(leds[led_index]), 100 * speed_scale)

            return leds

        except Exception as e:
            logger.error('_get_cpu_led_speeds: try error - [{}]'.format(e))
            sys.exit(RC_FAILED_CPU_MONIT_FETCH)
