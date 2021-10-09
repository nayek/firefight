import RPi.GPIO as GPIO
LED = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED,GPIO.OUT)
GPIO.output(LED,True)
