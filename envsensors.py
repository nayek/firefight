from mq import *
import sys
import time
import board
from adafruit_htu21d import HTU21D


print("Press CTRL+C to abort.")
#sys.stdout.write("Jeremy starting...")
mq = MQ();
# Create sensor object, communicating over the board's default I2C bus
i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = HTU21D(i2c)
#sys.stdout.write("Jeremy started")
while True:
    time.sleep(2)
    perc = mq.MQPercentage()
    sys.stdout.write("\r")
    sys.stdout.write("\033[K")
    #sys.stdout.write("Jeremy")
    sys.stdout.write("LPG: %g ppm, CO: %g ppm, Smoke: %g ppm Temp: %g H: %g" % (perc["GAS_LPG"], perc["CO"], perc["SMOKE"], sensor.temperature, sensor.relative_humidity))
    sys.stdout.flush()
    time.sleep(.1)
    


