#!/usr/bin/env python


import RPi.GPIO as GPIO
import subprocess
import I2C_LCD_driver


GPIO.setmode(GPIO.BCM)
GPIO.setup(3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.wait_for_edge(3, GPIO.FALLING)

mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_clear()
mylcd.backlight(0)
            
subprocess.call(['shutdown', '-h', 'now'], shell=False)
