import I2C_LCD_driver
import time
import max30100

mylcd = I2C_LCD_driver.lcd()
mx30 = max30100.MAX30100()

while True:
	mx30.set_mode(max30100.MODE_SPO2)
	mx30.read_sensor()
	mylcd.lcd_display_string("O2 {0} ".format(mx30.red/100),1)
	mylcd.lcd_display_string("HR {0}".format(mx30.ir/100),2)
	time.sleep(0.3)
