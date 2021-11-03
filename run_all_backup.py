import sys
import time
import board
import busio
import adafruit_tmp117
from adafruit_htu21d import HTU21D
import RPi.GPIO as GPIO
import I2C_LCD_driver
import max30100
from mq import *

#setup i2c and lcd
#i2c = board.I2C()
#i2c = busio.I2C(3,2)
#this isn't actually pins 45 and 44 it is pins GPIO27 and GPIO4 (see /boot/config.txt)
#circuitpython forces us to enter 45,44 so that it selects bus 10 automatically
#also had to change SMBUS to use 10 in MAX30100.py
i2c = busio.I2C(45,44)
mylcd = I2C_LCD_driver.lcd()

bodySensors = False
envSensors = False

tmp117 = None

mylcd.lcd_clear()
mylcd.lcd_display_string("Calibrating",1)

try:
    #connect to tmp 117
    tmp117 = adafruit_tmp117.TMP117(i2c)
    
    #connect to heartbeat monitor
    mx30 = max30100.MAX30100()
    mx30.set_mode(max30100.MODE_SPO2)
    
    bodySensors = True
except:
    bodySensors = False
 
#connect to env sensor
sensor = None
try:
    sensor = HTU21D(i2c)
    mq = MQ();
    
    envSensors = True
except:
    sensor = None
    
#setup alarm (temporary, move this)
ALERT = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(ALERT,GPIO.OUT)

starttime = time.time()
bodyValToPrint = 0;
envValToPrint = 0;
nCount=0

while True:
    bToggle = False;
    
    if time.time() - starttime > 2:
        bToggle = True;
        starttime = time.time()
    
    #print data for body sensors
    if not bodySensors:
        mylcd.lcd_display_string("No Body Sensors",1)
    else:
        mx30.read_sensor()
        if bToggle:
            if bodyValToPrint == 0:
                mylcd.lcd_display_string("Temp: {0:.2f} C".format(tmp117.temperature),1)
            elif bodyValToPrint == 1:
                mylcd.lcd_display_string("Max: {0:.2f} {1:.2f}".format(mx30.red,mx30.ir),1)
            bodyValToPrint = bodyValToPrint + 1
            if bodyValToPrint > 1:
                bodyValToPrint = 0;
        
#print data for environmental sensors        
    if not envSensors:
#        mylcd.lcd_display_string("No Env Sensors",2)
        #mylcd.lcd_display_string("HR {0:.2f} SP {1:.2f}".format(mx30.ir/1000/60,mx30.red),2)

       if mx30.ir > 7000:
           nCount = nCount + 1
           print("X: {0} Y: {1:.3f}".format(nCount,mx30.ir/100))
    else:
        perc = mq.MQPercentage()
        if bToggle:
            if envValToPrint == 0:
                mylcd.lcd_display_string("LPG: %.4f ppm" % (perc["GAS_LPG"]),2)
            elif envValToPrint == 1:
                mylcd.lcd_display_string("CO: %.4f ppm" % (perc["CO"]),2)
            elif envValToPrint == 2:
                mylcd.lcd_display_string("Smoke: %.4f ppm" % (perc["SMOKE"]),2)
            elif envValToPrint == 3:
                mylcd.lcd_display_string("Temp: %.2f H: %.2f" % (sensor.temperature, sensor.relative_humidity),2)
            envValToPrint = envValToPrint + 1
            if envValToPrint > 3:
                envValToPrint = 0;        

#set off alarms depending on readings
    if tmp117.temperature > 25:
        GPIO.output(ALERT,True)
        time.sleep(.05)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.05)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.05)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.05)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.3)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.5)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.2)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.4)
        GPIO.output(ALERT,False)
        time.sleep(.05)
        GPIO.output(ALERT,True)
        time.sleep(.6)
        GPIO.output(ALERT,False)
        
    if envSensors == True and perc["CO"] > 1:
        GPIO.output(ALERT,True)
        time.sleep(.1)
        GPIO.output(ALERT,False)
        time.sleep(.1)
        GPIO.output(ALERT,True)
        time.sleep(.1)
        GPIO.output(ALERT,False)
        time.sleep(.1)
        GPIO.output(ALERT,True)
        time.sleep(.1)
        GPIO.output(ALERT,False)
        time.sleep(.1)
        GPIO.output(ALERT,True)
        time.sleep(.1)
        GPIO.output(ALERT,False)
        time.sleep(.1)
        GPIO.output(ALERT,True)
        time.sleep(.1)
        GPIO.output(ALERT,False)
        time.sleep(.1)
        GPIO.output(ALERT,True)
        time.sleep(.1)
        GPIO.output(ALERT,False)
        time.sleep(.1)

    GPIO.output(ALERT,False)
