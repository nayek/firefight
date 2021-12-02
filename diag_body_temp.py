#general libraries
import sys
import time

#libraries for general access to i2c using circuitpython
import board
import busio

#library for tmp117 sensor
import adafruit_tmp117

#library for htu21d sensor
from adafruit_htu21d import HTU21D

#library for direct access to GPIO pins
import RPi.GPIO as GPIO

#library for LCD
import I2C_LCD_driver

#library for max30100
import max30100

#library for mlx90614
import adafruit_mlx90614

#library for gas sensors
from mq import *

#####Init Variables######
#
# Initializing all global variables to be used here
#
#########################

nUpdateTimerSec = 5
nHeartBeatTimerSec = 1

#Default all sensors to not present
bLCDPresent = False
bI2CLibPresent = False
bBodyMaxPresent = False
bBodyTempPresent = False
bBodyIRPresent = False
bEnvO2Present = False
bEnvTempPresent = False
bOurAlarmPresent = False
bOtherAlarmPresent = False
bToggle = False
bUpdateDisplay = False
bHeartBeat = False
nDisplay = 0

#Default all sensors text to NA
sBodyO2Text = "CA"
sBodyHBText = "CA"
sBodyTempText = "CA"
sBodyIRText = "CA"
sEnvCOText = "CA"
sEnvTempText = "CA"
sEnvRHText = "CA"
sOurAlarmText = "CA"
sOtherAlarmText = "CA"

#Full text displays
sFullBodyO2Text = "NA"
sFullBodyHBText = "NA"
sFullBodyTempText = "NA"
sFullBodyIRText = "NA"
sFullEnvCOText = "NA"
sFullEnvTempText = "NA"
sFullEnvRHText = "NA"
sFullEnvLPGText = "NA"
sFullEnvSmokeText = "NA"

#Timers used for various timing functions
lastupdatetime = time.time()
lasthbtime = time.time()
    
#####Init Hardware######
#
# Initializing all global hardware here
#
########################
mylcd = None
tmp117 = None
mx30 = None
i2c = None
htu21d = None
mq = None
mlx = None
    
#setup alarm (temporary, move this)
ALERT = 22
TOGGLE = 14
HEARTBEAT = 15

GPIO.setmode(GPIO.BCM)
GPIO.setup(ALERT,GPIO.OUT)
GPIO.setup(HEARTBEAT,GPIO.OUT)

GPIO.setup(TOGGLE,GPIO.IN,pull_up_down=GPIO.PUD_UP)


def myInterrupt(channel):
    if not bToggle:
        toggleDisplay()
    
#setup the i2c lib used in adafruit devices
def UpdateI2CLib(bForceInit):
    global bI2CLibPresent
    global i2c
    
    try:
        if (not bI2CLibPresent or bForceInit):
            #setup i2c--this isn't actually pins 45 and 44 it is pins GPIO27 and GPIO4 (see /boot/config.txt)
            #circuitpython forces us to enter 45,44 so that it selects bus 10 automatically
            #also had to change SMBUS to use 10 in MAX30100.py
            i2c = busio.I2C(45,44)
            #i2c = smbus.SMBus(port) #would this work?
            bI2CLibPresent = True
    except:
            bI2CLibPresent = False

def UpdateEnvTempAndHumity(bForceInit):
    global bEnvTempPresent
    global htu21d
    global sEnvTempText
    global sEnvRHText
    global sFullEnvTempText
    global sFullEnvRHText
    try:
        #init i2c lib if needed
        UpdateI2CLib(False)
        
        if (not bEnvTempPresent or bForceInit):
            htu21d = HTU21D(i2c)
            bEnvTempPresent = True

        sEnvTempText = "{0:2f}".format(htu21d.temperature)
        sEnvRHText = "{0:2f}".format(htu21d.relative_humidity)
        sFullEnvTempText = "Env Temp: {0:.2f}C".format(htu21d.temperature)
        sFullEnvRHText = "Env RH: {0:.2f}%".format(htu21d.relative_humidity)
    except:
        bEnvTempPresent = False
        sFullEnvTempText = "Env Temp: NA"
        sFullEnvRHText = "Env RH: NA"
        if sEnvTempText == ".-":
            sEnvTempText = "-."
            sEnvRHText = "-."
        else:
            sEnvTempText = ".-"
            sEnvRHText = ".-"

#setup the body temp tmp117 sensor and/or pull latest data
def UpdateBodyTemp(bForceInit):
    global bBodyTempPresent
    global tmp117
    global sBodyTempText
    global sFullBodyTempText
    try:
        #init i2c lib if needed
        UpdateI2CLib(False)
        
        if (not bBodyTempPresent or bForceInit):
            tmp117 = adafruit_tmp117.TMP117(i2c)
            bBodyTempPresent = True
            
        sBodyTempText = "{0:2f}".format(tmp117.temperature)
        sFullBodyTempText = "Body Temp: {0:.2f}C".format(tmp117.temperature)
    except:
        bBodyTempPresent = False
        sFullBodyTempText = "Body Temp: NA"
        if sBodyTempText == ".-":
            sBodyTempText = "-."
        else:
            sBodyTempText = ".-"   

#setup the body temp tmp117 sensor and/or pull latest data
def UpdateBodyIRSensor(bForceInit):
    global bBodyIRPresent
    global mlx
    global sBodyIRText
    global sFullBodyIRText
    try:
        #init i2c lib if needed
        UpdateI2CLib(False)
        
        if (not bBodyIRPresent or bForceInit):
            mlx = adafruit_mlx90614.MLX90614(i2c)
            bBodyIRPresent = True
            
        sBodyIRText = "{0:2f}".format(mlx.ambient_temperature)
        sFullBodyIRText = "T: {0:.2f} {1:.2f}".format(mlx.object_temperature,mlx.ambient_temperature)
        print(sFullBodyIRText)
    except:
        bBodyIRPresent = False
        sFullBodyIRText = "IR Data: NA"
        if sBodyIRText == ".-":
            sBodyIRText = "-."
        else:
            sBodyIRText = ".-"   

def UpdateEnvGasSensors(bForceInit):
    global sEnvCOText
    global sFullEnvCOText
    global sFullEnvLPGText
    global sFullEnvSmokeText
    global bEnvO2Present
    global mx30
    global mq
    
    try:
        #if we need initialized, try to initialize
        if not bEnvO2Present or bForceInit:
            #connect to heartbeat/02 monitor
            print("mq init? {0}".format(bEnvO2Present))
            mq = MQ()
            
            bEnvO2Present = True
        
        #read sensor and set values if available
        perc = mq.MQPercentage()

        sEnvCOText = "{0:2f}".format(perc["CO"])
        sFullEnvCOText = "CO: {0:.4f}ppm".format(perc["CO"])
        sFullEnvLPGText = "LPG: {0:.4f}ppm".format(perc["GAS_LPG"])
        sFullEnvSmokeText = "Smoke: {0:.4f}ppm".format(perc["SMOKE"])

    except Exception as e:
        print("mq error {0}".format(e))
        bEnvO2Present = False
        sFullEnvCOText = "CO: NA"
        sFullEnvLPGText = "LPG: NA"
        sFullEnvSmokeText = "Smoke: NA"
        #dumb code to flip the dot so we can see its processing but not there
        if sEnvCOText == ".-":
            sEnvCOText = "-."
        else:
            sEnvCOText = ".-"

def ProcessMaxData(red,ir):
    O2Data = red /1000
    HBData = ir / 1000
    
    return O2Data, HBData

def UpdateBodyMaxSensors(bForceInit):
    global sBodyO2Text
    global sBodyHBText
    global sFullBodyO2Text
    global sFullBodyHBText
    global bBodyMaxPresent
    global mx30
    
    try:
        #if we need initialized, try to initialize
        if not bBodyMaxPresent or bForceInit:
            #connect to heartbeat/02 monitor
            mx30 = max30100.MAX30100()
            mx30.set_mode(max30100.MODE_SPO2)
            
            bBodyMaxPresent = True
        
        #read sensor and set values if available
        mx30.read_sensor()
        O2Text, HBText = ProcessMaxData(mx30.red, mx30.ir)
        sBodyO2Text = "{0:2f}".format(O2Text)
        sBodyHBText = "{0:2f}".format(HBText)
        sFullBodyO2Text = "Body O2: {0:.2f}ppm".format(O2Text)
        sFullBodyHBText = "Body HB: {0:.2f}bpm".format(HBText)
    except:        
        bBodyMaxPresent = False
        sFullBodyO2Text = "Body O2: NA"
        sFullBodyHBText = "Body HB: NA"
        
        if sBodyO2Text == ".-":
            sBodyO2Text = "-."
            sBodyHBText = "-."
        else:
            sBodyO2Text = ".-"
            sBodyHBText = ".-"

def toggleDisplay():
    global bToggle
    global lastupdatetime
    bToggle = True

    lastupdatetime = time.time()

     
#setup LCD
def UpdateLCD(bForceInit):
    global bLCDPresent
    global mylcd
    global bToggle
    global nDisplay
    
    try:
        if (not bLCDPresent or bForceInit):
            mylcd = I2C_LCD_driver.lcd()
            bLCDPresent = True
            mylcd.lcd_clear()
            mylcd.lcd_display_string("PRJ Industries",1)
            mylcd.lcd_display_string("Calibrating...",2)
        elif not bToggle:
            #make sure the 2 lines are only 16 chars
            sTopLine =    "{0:.2s} {1:.2s} {2:.2s}      {3:.2s}".format(sBodyO2Text,sBodyHBText,sBodyTempText,sOurAlarmText)
            sBottomLine = "{0:.2s} {1:.2s} {2:.2s} {3:.2s}   {4:.2s}".format(sEnvCOText,sEnvTempText,sEnvRHText,sBodyIRText,sOtherAlarmText)
            mylcd.lcd_clear()
            mylcd.lcd_display_string(sTopLine,1)
            mylcd.lcd_display_string(sBottomLine,2)
        else:
            mylcd.lcd_clear()
            if nDisplay == 0:
                mylcd.lcd_display_string(sFullBodyO2Text,1)
                mylcd.lcd_display_string(sFullBodyHBText,2)
                #GPIO.output(ALERT,True)
            elif nDisplay == 1:
                mylcd.lcd_display_string(sFullBodyTempText,1)
                mylcd.lcd_display_string(sFullEnvCOText,2)
                #GPIO.output(ALERT,False)
            elif nDisplay == 2:
                mylcd.lcd_display_string(sFullEnvTempText,1)
                mylcd.lcd_display_string(sFullEnvRHText,2)
                #GPIO.output(ALERT,True)
            elif nDisplay == 3:
                mylcd.lcd_display_string(sFullBodyIRText,1)
                mylcd.lcd_display_string(sFullEnvLPGText,2)
                #GPIO.output(ALERT,False)
            elif nDisplay == 4:
                mylcd.lcd_display_string(sFullEnvSmokeText,1)
                mylcd.lcd_display_string("End Report",2)
            else: #dont ever show this
                mylcd.lcd_display_string("Hi Dr. Proano",1)
                mylcd.lcd_display_string("I am Error",2)
                print("ndisplay {0}".format(nDisplay))

            nDisplay = nDisplay + 1
            print(nDisplay)
            if nDisplay > 4: #reset display
                nDisplay = 0
                
            bToggle = False
    except Exception as e:
        bLCDPresent = False
        mylcd.lcd_display_string("Error",1)
        bToggle = False
        print(e)
        if nDisplay > 5: #reset display
                nDisplay = 0
    
#main processing function
def main():
    global lastupdatetime
    global lasthbtime
    global bHeartBeat
    global nDisplay
    global bToggle
    
    GPIO.add_event_detect(TOGGLE,GPIO.FALLING,callback=myInterrupt,bouncetime=250)

    #update the LCD right away so we aren't waiting for 5 seconds
    UpdateLCD(False)   
    
    while True:
        if time.time() - lasthbtime > nHeartBeatTimerSec:
            #update heartbeat
            bHeartBeat = ~bHeartBeat
            GPIO.output(HEARTBEAT,bHeartBeat)
            lasthbtime = time.time()
            
        #timer to update stuff
        if time.time() - lastupdatetime < nUpdateTimerSec:
            if bToggle:
                UpdateLCD(False)
            continue
        
        #if we have waited 5 seconds then we are ok to disable toggle and reset our display
        bToggle = False
        nDisplay = 0
        
        #go out and try to get sensor data
        UpdateBodyMaxSensors(False)
        UpdateBodyTemp(False)
        UpdateBodyIRSensor(False)
        UpdateEnvTempAndHumity(False)
        UpdateEnvGasSensors(False)
        
        #now update our screen
        UpdateLCD(False)
        
        
        
        #reset timer
        lastupdatetime = time.time()
              
    #set off alarms depending on readings
        
        #GPIO.output(ALERT,False)
    
#python-wython stuff to force main to be called when running this as a program    
if __name__ == '__main__':
    main()