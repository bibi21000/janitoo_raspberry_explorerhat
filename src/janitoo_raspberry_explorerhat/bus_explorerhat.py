# -*- coding: utf-8 -*-
"""The Raspberry i2c bus

"""

__license__ = """
    This file is part of Janitoo.

    Janitoo is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Janitoo is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Janitoo. If not, see <http://www.gnu.org/licenses/>.

"""
__author__ = 'Sébastien GALLET aka bibi21000'
__email__ = 'bibi21000@gmail.com'
__copyright__ = "Copyright © 2013-2014-2015-2016 Sébastien GALLET aka bibi21000"

# Set default logging handler to avoid "No handler found" warnings.
import logging
logger = logging.getLogger(__name__)
import os, sys
import threading
import time
import datetime
import socket

from janitoo.thread import JNTBusThread
from janitoo.bus import JNTBus
from janitoo.component import JNTComponent
from janitoo.thread import BaseThread
from janitoo.options import get_option_autostart

# ~ import Adafruit_GPIO.I2C as I2C

from janitoo_raspberry_explorerhat import OID

##############################################################
#Check that we are in sync with the official command classes
#Must be implemented for non-regression
from janitoo.classes import COMMAND_DESC

COMMAND_CAMERA_PREVIEW = 0x2200
COMMAND_CAMERA_PHOTO = 0x2201
COMMAND_CAMERA_VIDEO = 0x2202
COMMAND_CAMERA_STREAM = 0x2203

assert(COMMAND_DESC[COMMAND_CAMERA_PREVIEW] == 'COMMAND_CAMERA_PREVIEW')
assert(COMMAND_DESC[COMMAND_CAMERA_PHOTO] == 'COMMAND_CAMERA_PHOTO')
assert(COMMAND_DESC[COMMAND_CAMERA_VIDEO] == 'COMMAND_CAMERA_VIDEO')
assert(COMMAND_DESC[COMMAND_CAMERA_STREAM] == 'COMMAND_CAMERA_STREAM')
##############################################################

class ExplorerHatBus(JNTBus):
    """A pseudo-bus to handle the Raspberry I2C Bus
    """

    def __init__(self, **kwargs):
        """
        :param int bus_id: the SMBus id (see Raspberry Pi documentation)
        :param kwargs: parameters transmitted to :py:class:`smbus.SMBus` initializer
        """
        # ~ self.kernel_modprobe('i2c-dev')
        # ~ self.kernel_modprobe('i2c-bcm2708')
        # ~ JNTBus.__init__(self, **kwargs)
        # ~ self._i2c_lock = threading.Lock()
        # ~ self.load_extensions(OID)
        # ~ self._ada_i2c = I2C
        # ~ """ The shared ADAFruit I2C bus """
        # ~ self.export_attrs('i2c_acquire', self.i2c_acquire)
        # ~ self.export_attrs('i2c_release', self.i2c_release)
        # ~ self.export_attrs('get_i2c_device', self.get_i2c_device)
        # ~ self.export_attrs('get_busnum', self.get_busnum)
        # ~ self.export_attrs('get_adafruit_i2c', self.get_adafruit_i2c)
        # ~ self.export_attrs('software_reset', self.software_reset)
        # ~ self.export_attrs('require_repeated_start', self.require_repeated_start)

        uuid="%s_busnum"%OID
        self.values[uuid] = self.value_factory['config_integer'](options=self.options, uuid=uuid,
            node_uuid=self.uuid,
            help='The I2C bus number to use. Set it to None to get default bus',
            label='BusNum',
            default=None,
        )

    def exphat_acquire(self, blocking=True):
        """Get a lock on the bus"""
        if self._i2c_lock.acquire(blocking):
            return True
        return False

    def exphat_release(self):
        """Release a lock on the bus"""
        self._i2c_lock.release()

    def get_busnum(self):
        """Get the bus num depending of the plateform"""
        if self.values["%s_busnum"%OID].data is None:
            return self._ada_i2c.get_default_bus()
        return self.values["%s_busnum"%OID].data

    def get_adafruit_exphat(self):
        """Get the I2C interface from adafruit"""
        return self._ada_i2c

    def get_exphat_device(self, address, **kwargs):
        """Get the device at address"""
        return self._ada_i2c.get_i2c_device(address, busnum=self.get_busnum(), i2c_interface=self._ada_i2c, **kwargs )

    def require_repeated_start(self):
        """Get the default bus num depending of the plateform"""
        return self._ada_i2c.require_repeated_start()

    def software_reset(self):
        "Sends a software reset (SWRST) command to all the servo drivers on the bus"
        general_call_i2c = self.get_i2c_device(0x00)
        general_call_i2c.writeRaw8(0x06)        # SWRST
