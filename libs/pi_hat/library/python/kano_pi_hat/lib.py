#
# lib.py
#
# Copyright (C) 2017-2018 Kano Computing Ltd.
# License: http://www.gnu.org/licenses/gpl-2.0.txt GNU GPL v2
#
# Loader for the dynamic library interface
#


import os
import ctypes

HAT_LIB = 'libkano_hat.so'


def load_libkano_hat():
    try:
        libkano_hat = ctypes.CDLL(HAT_LIB)
    except OSError:
        local_dir = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..', '..', HAT_LIB)
        )
        libkano_hat = ctypes.CDLL(local_dir)

    return libkano_hat
