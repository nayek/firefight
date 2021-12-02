import I2C_LCD_driver
import time
import max30100

mylcd = I2C_LCD_driver.lcd()
mx30 = max30100.MAX30100()
#mx30.set_mode(max30100.MODE_SPO2)
mx30.enable_spo2()

while True:
    mx30.read_sensor()

    mx30.ir,mx30.red
    
    hb = int(mx30.ir)
    #spo2 = int(mx30.red / 100)

    #if mx30.ir != mx30.buffer_ir:
    print("pulse: ",hb)
    #if mx30.red != mx30.buffer_red:
    #    print("spo2: ",spo2)

    time.sleep(.1)
    #mylcd.lcd_display_string("O2 {0} ".format(mx30.red/100),1)
    #mylcd.lcd_display_string("HR {0}".format(mx30.ir/100),2)

