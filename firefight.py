import I2C_LCD_driver
import time
import board
import adafruit_tmp117
import max30100
#import adafruit_si7021
import smbus
#from pi_si7021 import Si7021

i2c = board.I2C()
tmp117 = adafruit_tmp117.TMP117(i2c)
mylcd = I2C_LCD_driver.lcd()
#sensor = adafruit_si7021.SI7021(i2c) 
bus = smbus.SMBus(1)
#RHTEMP = Si7021()
mx30 = max30100.MAX30100()



while True:
	mylcd.lcd_display_string("%.2f C %.2f IR".format(tmp117.temperature,mx30.ir),1)
#	mylcd.lcd_display_string("%.2f RH"%str(round(RHTEMP.relative_humidity,2)),2)

	bus.write_byte(0x40,0xF5)
	time.sleep(0.3)
	data0 = bus.read_byte(0x40)
	#data1 = bus.read_byte(0x40)
	#time.sleep(0.3)
	#data1 = bus.read_byte(0x40)
	#humidity = ((data0 * 256 + data1) * 125 / 65536.0) -6
	humidity = ((data0 * 256) * 125 /65536.0) - 6	
#	mylcd.lcd_display_string("PRJ Tech Firefight 1.0",2)
	bus.write_byte(0x40,0xF3)
	time.sleep(0.3)
	data0 = bus.read_byte(0x40)
#	data1 = bus.read_byte(0x40)
	celsTemp = ((data0 * 256) * 175.72 / 65536.0) - 46.85
	mx30.read_sensor()
	
	mylcd.lcd_display_string('{0:2.1f} RH {1:2.1f} C'.format(humidity,celsTemp),2)
