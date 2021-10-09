import I2C_LCD_driver
from time import *

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_display_string("PRJ Technologies", 1)
mylcd.lcd_display_string("Firefight 1.0", 2)