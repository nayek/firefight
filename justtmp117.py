import time
import board
import busio
import adafruit_tmp117

#i2c = board.I2C()
i2c = busio.I2C(45,44)
tmp117 = adafruit_tmp117.TMP117(i2c)

while True:
	print("Temperature: %.2f degrees C"%tmp117.temperature)
	time.sleep(1)
