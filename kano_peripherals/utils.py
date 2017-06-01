# utils.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Helper and utility functions.


import time
import dbus
import traceback
import dbus.exceptions

from kano.logging import logger

from kano_peripherals.paths import BUS_NAME, SERVICE_MANAGER_OBJECT_PATH, \
    SERVICE_MANAGER_IFACE


def get_service_manager_interface(retry_count=5, retry_time_sec=1):
    """
    Helper function to obtain a DBus interface to the ServiceManger.

    Args:
        retry_count    - int number of times to retry after first attempt failed.
        retry_time_sec - int time in seconds to sleep in between retries.

    Returns:
        iface - dbus.Interface object to reach the DBus service, None on failure.
    """
    return get_service_interface(
        SERVICE_MANAGER_OBJECT_PATH,
        SERVICE_MANAGER_IFACE,
        retry_count=retry_count,
        retry_time_sec=retry_time_sec
    )


def get_service_interface(object_path, object_iface, retry_count=5, retry_time_sec=1):
    """
    Helper function to obtain a DBus interface to a specified service.
    NOTE: Currently, this is NOT suited for use outside of this project.

    Args:
        object_path    - str path to the DBus service object, e.g. /me/kano/boards/ServiceManager
        object_iface   - str interface to the DBus service, e.g. me.kano.boards.ServiceManager
        retry_count    - int number of times to retry after first attempt failed.
        retry_time_sec - int time in seconds to sleep in between retries.

    Returns:
        iface - dbus.Interface object to reach the DBus service, None on failure.
    """
    iface = None
    successful = False
    retry_count = max(0, int(retry_count))

    for retry in range(0, 1 + retry_count):
        try:
            iface = dbus.Interface(
                dbus.SystemBus().get_object(BUS_NAME, object_path),
                object_iface
            )

            # Test if the service is online with a simple method call. If the service
            # replies back and the method returns, it's available.
            iface.hello_world()
            successful = True
            break

        except dbus.exceptions.DBusException, dbus.exceptions.UnknownMethodException:
            if retry_count:
                time.sleep(retry_time_sec)
            logger.warn(
                'utils: get_service_interface: Retring for {}, got exception:\n{}'
                .format(object_iface, traceback.format_exc())
            )
            continue
        except Exception:
            logger.error(
                'utils: get_service_interface: For {}, unexpected error occured:\n{}'
                .format(traceback.format_exc())
            )
            break

    if not iface or not successful:
        logger.warn(
            'DBus iface not found for {}. Is kano-boards-daemon running?'
            .format(object_iface)
        )
        return None

    return iface
