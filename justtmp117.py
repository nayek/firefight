import time
import board
import adafruit_tmp117

i2c = board.I2C()
tmp117 = adafruit_tmp117.TMP117(i2c)

while True:
	print("Temperature: %.2f degrees C"%tmp117.temperature)
	time.sleep(1)
