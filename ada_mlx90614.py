#MIT License
#
#Copyright (c) 2018 Bill Simpson
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
"""
`MLX90614` - MLX90614 I2C IR Temperature Sensor
====================================================
CircuitPython library to support MLX90614 IR temperature sensor.
Adapted from standard Adafruit drivers
Author: Bill Simpson
"""

_I2C_ADDR = const(0x5a)        # I2C address for the sensor

_REGISTER_TA = const(0x06)     # ambient
_REGISTER_TOBJ1 = const(0x07)  # object
_REGISTER_TOBJ2 = const(0x08)  # object2 (if dual zone sensor)

_REGISTER_EMISS = const(0x24)  # emissivity 
_REGISTER_CONFIG1 = const(0x25) # configuration

from adafruit_bus_device.i2c_device import I2CDevice


class MLX90614:
    """Interface to the MLX90614 temperature sensor."""

    def __init__(self, i2c_bus, device_address=_I2C_ADDR):
        self.i2c_device = I2CDevice(i2c_bus, device_address)
        self.buf = bytearray(2) # create buffer for transfer (2 bytes)

        self.buf[0] = _REGISTER_CONFIG1
        with self.i2c_device as i2c:
            i2c.write(self.buf, end=1, stop=False)
            i2c.readinto(self.buf)
        print ('config1 byte 0: '+bin(self.buf[0]))
        print ('config1 byte 1: '+bin(self.buf[1]))
        if (self.buf[1] & (1 << 6)):
            print ('sensor is dualzone')
            self.dualzone = True
        else:
            self.dualzone = False
    
    @property
    def temp_amb_c(self):
        """Ambient (case) Temperature in celsius. Read-only."""
        self.buf[0] = _REGISTER_TA
        with self.i2c_device as i2c:
            i2c.write(self.buf, end=1, stop=False)
            i2c.readinto(self.buf)
        return self._temp_conv_c()

    @property
    def temp_obj_c(self):
        """Object Temperature in celsius. Read-only."""
        self.buf[0] = _REGISTER_TOBJ1
        with self.i2c_device as i2c:
            i2c.write(self.buf, end=1, stop=False)
            i2c.readinto(self.buf)
        return self._temp_conv_c()

    @property
    def temp_obj2_c(self):
        """Second Object Temperature in celsius. Read-only."""
        if self.dualzone:
            self.buf[0] = _REGISTER_TOBJ2
            with self.i2c_device as i2c:
                i2c.write(self.buf, end=1, stop=False)
                i2c.readinto(self.buf)
            return self._temp_conv_c()
        else:
            return float('nan')

    def _temp_conv_c(self):
        """Raw to C temp conversion"""
        value = self.buf[1] << 8 | self.buf[0]
        return ((value * 0.02) - 273.15)
