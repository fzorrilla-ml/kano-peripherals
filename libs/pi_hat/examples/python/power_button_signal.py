#!/usr/bin/env python
#
# power_button_signal.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPLv2
#
# Interfacing with the power button through the high-level interface
#


import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib

from kano_peripherals.paths import PI_HAT_OBJECT_PATH, PI_HAT_IFACE, \
    BUS_NAME as PI_HAT_BUS_NAME


def power_pressed_cb():
    print 'Power button pressed'


if __name__ == '__main__':
    DBusGMainLoop(set_as_default=True)

    '''
    Connect to DBus signal:
        Bus: System
        Bus Name: me.kano.boards
        Interface: me.kano.boards.PiHat
        Object Path: /me/kano/boards/PiHat
        Signal: power_button_pressed
    '''
    dbus.SystemBus().add_signal_receiver(
        power_pressed_cb, 'power_button_pressed', PI_HAT_IFACE,
        PI_HAT_BUS_NAME, PI_HAT_OBJECT_PATH
    )

    GLib.MainLoop().run()
