# return_codes.py
#
# Copyright (C) 2017 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# The expected exit codes for binaries in this project.


RC_SUCCESSFUL = 0

RC_INCORRECT_ARGUMENTS = 11
RC_NO_BOARD_DETECTED = 12
RC_SECOND_INSTANCE = 13
RC_UNKNOWN_EXCEPTION = 14
RC_FAILED_STOP_DAEMON = 15

RC_FAILED_LOCKING_API = 21
RC_FAILED_ANIM_GET_DBUS = 22
RC_FAILED_CPU_MONIT_FETCH = 23
RC_FAILED_UNLOCKING_API = 24

RC_KANO_LED_SPEAKER_DETECTED = 51
RC_KANO_PI_HAT_DETECTED = 52
RC_KANO_POWER_HAT_DETECTED = 53
