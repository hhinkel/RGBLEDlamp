from machine import Pin
import time
import neopixel

pin = 27
num = 144

#Create noepixel object
#For ESP32
strip = neopixel.NeoPixel(Pin(pin), num)
#For ESP8266
#strip = neopixel.NeoPixel(machine.Pin(pin), num)

#RGB values commented by the approximate Temp in Kelvin
temp = (255, 249, 253)
#kelvin_list = (
#    (255, 228, 206), #5000
#    (255, 230, 210), #5100
#    (255, 232, 213), #5200
#    (255, 233, 217), #5300
#    (255, 235, 220), #5400
#    (255, 236, 224), #5500
#    (255, 238, 227), #5600
#    (255, 239, 230), #5700
#    (255, 240, 233), #5800
#    (255, 242, 236), #5900
#    (255, 243, 239), #6000
#    (255, 244, 242), #6100
#    (255, 245, 245), #6200
#    (255, 246, 247), #6300
#    (255, 248, 251), #6400
#    (255, 249, 253)) #6500

def clear():
    strip.fill((0, 0, 0))
    strip.write()
    
def setColor(temp):
    strip.fill(temp)
    strip.write()

def fade(startColor, endColor, steps, interval):
    lastUpdate = time.time() - interval
    
    for i in range(0, steps):
        red = ((startColor[0] * (steps - i)) + (endColor[0] * i)) // steps
        green = ((startColor[1] * (steps - i)) + (endColor[1] * i)) // steps
        blue = ((startColor[2] * (steps - i)) + (endColor[2] * i)) // steps
        
        while ((time.time() - lastUpdate) < interval):
            pass
        
        color = (red, green, blue)
        setColor(color)
        
        lastUpdate = time.time()
            

clear()
lastUpdate = time.time() - 30
fade((0,0,0), temp, 60, 0.02)
while ((time.time() - lastUpdate) < 30):
    pass
fade(temp, (0,0,0), 60, 0.02)
clear()
lastUpdate = time.time()
    
    
