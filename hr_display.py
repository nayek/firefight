import max30100
import threading
import time
import numpy as np
#library for direct access to GPIO pins
import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import matplotlib.animation as animation

HEARTBEAT = 15
GPIO.setmode(GPIO.BCM)
GPIO.setup(HEARTBEAT,GPIO.OUT)

sensor = max30100.MAX30100()
sensor.enable_spo2()

MAX_HISTORY = 250
TOTAL_BEATS = 30

def calculate_bpm(beats):
    # Truncate beats queue to max, then calculate bpm.
    # Calculate difference in time from the head to the
    # tail of the list. Divide the number of beats by
    # this duration (in seconds)
    beats = beats[-TOTAL_BEATS:]
    beat_time = beats[-1] - beats[0]
    if beat_time:
        bpm = (len(beats) / (beat_time)) * 60
        print("%d bpm"%bpm)
        
        

# Maintain a log of previous values to
# determine min, max and threshold.
history = []
mod_history = []
beats = []

plt.ion()

fig = plt.figure()

ax = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

sensor.enable_spo2()
beatOn = False

ncount = 0

while True:
    time.sleep(.015)
    ncount = ncount + 1
    sensor.read_sensor()
    v = sensor.ir 
    if(v < 18000):
        continue
    
    history.append(v)

    # Get the tail, up to MAX_HISTORY length
    history = history[-MAX_HISTORY:]
    
    minima, maxima = min(history), max(history)
    
    beat_range = (maxima - minima) * .48

    beat_point = maxima - beat_range
    rest_point = maxima - (beat_range * 1.2)
    
    if v > beat_point and beatOn == False:
        mod_history.append(1)
        GPIO.output(HEARTBEAT,True)
        beats.append(time.time())
        beats = beats[-TOTAL_BEATS:]
        calculate_bpm(beats)
        beatOn = True
    elif v < rest_point and beatOn == True:
        mod_history.append(-1)
        GPIO.output(HEARTBEAT,False)
        beatOn = False
    else:
        mod_history.append(0)

        
    mod_history = mod_history[-MAX_HISTORY:]
                       
    if mod_history[-1] > 0:
        threshold_on = True
    else:
        threshold_on = False
        
    if(ncount > 50):
        ncount = 0
        x = range(len(mod_history))
        ax.cla()
        line1, = ax.plot(x,mod_history,'r-')
        line1.set_ydata(mod_history)
        plt.ylim(-2,2)
        
        ax2.cla()
        x = range(len(history))

        line1, = ax2.plot(x,history,'r-')
        line1.set_ydata(history)

        fig.canvas.draw()
        fig.canvas.flush_events()
 
        
    #time.sleep(.015 )
       


