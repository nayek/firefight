import time
import board
import adafruit_tmp117
import RPi.GPIO as GPIO
import I2C_LCD_driver
import max30100

i2c = board.I2C()
tmp117 = adafruit_tmp117.TMP117(i2c)
mylcd = I2C_LCD_driver.lcd()
ALERT = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(ALERT,GPIO.OUT)
mx30 = max30100.MAX30100()
mx30.set_mode(max30100.MODE_SPO2)

while True:
	mx30.read_sensor()
	print("Temp: %.2f degrees C"%tmp117.temperature)
	print("Max: {0} {1}".format(mx30.red/100, mx30.ir/100))
	mylcd.lcd_display_string("Temp: {0:.2f} C".format(tmp117.temperature),1)
	mylcd.lcd_display_string("Max: {0} {1}".format(mx30.red/100,mx30.ir/100),2)
	time.sleep(1)
	if tmp117.temperature > 25:
		GPIO.output(ALERT,True)
	else:
		GPIO.output(ALERT,False)
