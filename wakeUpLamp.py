''' Copyright 2021 Heidi Hinkel 

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE. '''

import machine
import sys
import network
import utime
import ntptime
import uasyncio
import neopixel

#User constants
SSID = 'SSID'
PW = 'password'
TIME_ZONE = -4   #hours from GMT. This is EDT (-5 is EST)
SEC_IN_HOUR = 3600 #Seconds in an hour
LIT_LENGTH = 2 #Hours at brightest setting 
WAKEUP_TUPLE = (4, 45)  #time lights come on in 24hr format, hour and minute
PIN = 27 #Pin that connects the lights to the microcontroller
NUM_NEOPIXELS = 50 #Number of neopixels to turn on in the strip
LED_COLOR_FULL = (255, 255, 255) #RGB values for LEDs when fully on
LED_COLOR_RED = (100, 0, 0) #RGB values for LEDs red only for error signaling
LED_COLOR_BLUE = (0, 0, 100)
LED_COLOR_OFF = (0, 0, 0) #RGB values for LEDs when off

#RGB values commented by the approximate Temp in Kelvin
#From this web site https://andi-siess.de/rgb-to-color-temperature/
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

async def setup(strip):
    """ Test the LEDs, set the clock for the first time and get the wake up time.
    Arguments:
        strip - neopixel object
    Local Variables:
        None
    Returns:
        Nothing """
    for i in range(0, 3):
        ledFlash(strip, LED_COLOR_FULL)
    updateRTCFromNTP(strip)

def ledFlash(strip, color, t = 1):
    """ Bring neopixel strip to full and then clear it
    Arguments:
        strip - neopixel object
        color - tuple containing RGB values for the neopixels
        t - time to wait between turning on the LEDs and turning them off
    Local Variables:
        None
    Returns:
        Nothing """
    utime.sleep(t)
    setStrip(strip, color)
    utime.sleep(t)
    setStrip(strip, LED_COLOR_OFF)

def clearStrip(strip):
    """ Bring neopixel strip to full
    Arguments:
        strip - neopixel object
    Local Variables:
        None
    Returns:
        Nothing """
    strip.fill(LED_COLOR_OFF)
    strip.write()
     
def setStrip(strip,temp):
    """ Bring neopixel strip to full
    Arguments:
        strip - neopixel object
    Local Variables:
        None
    Returns:
        Nothing """
    strip.fill(temp)
    strip.write()

def updateRTCFromNTP(strip):
    """ Update the microcontrollers real time clock (RTC) from
        network time protocol (NTP) servers. The RTC of the ESP8266 is notoriously inaccurate.
        https://docs.micropython.org/en/latest/esp8266/general.html#real-time-clock
    Arguments:
        strip - noepixel object (for flashing if can not connect to NTP server)
    Local Variables:
        wifi - wifi object
        localTime - as a time tuple (see setup)
    Returns:
        Nothing """
    wifi = connectToWifi(strip)
    try:
        ntptime.settime()
    except OSError:
        for i in range(0, 3):
            ledFlash(strip, LED_COLOR_RED, 0.5)
        print("Can not connect to NTP server")
        machine.reset()
    localTime = getLocalTime() 
    print("Local time after synchronization：%s" %str(localTime))
    disconnectFromWifi(wifi)

def connectToWifi(strip):
    """ Setup the wifi object and connect to the network defined above
    Arguments:
        strip - neopixel object
    Local Variables:
        wifi - network object
    Returns:
        wifi - network object """
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID,PW)
    while not wifi.isconnected():
        ledFlash(strip, LED_COLOR_BLUE, 0.5)
        pass
    return wifi

def disconnectFromWifi(wifi):
    """ Disconnect from wifi
    Arguments:
        wifi - network object
    Local Variables:
        None
    Returns:
        Nothing """
    wifi.disconnect()
    wifi.active(False)

def getLocalTime():
    """ Get local Time
    Arguments:
        None
    Local Variables:
        None
    Returns:
        local time tuple """
    return (utime.localtime(utime.time() + TIME_ZONE * SEC_IN_HOUR))

def createNeoPixelObject():
    """ Create the Neopixel object
    Arguments:
        None
    Local Variables:
        None
    Returns:
        Neopixel object """
    return neopixel.NeoPixel(machine.Pin(PIN), NUM_NEOPIXELS)

async def clock(strip):
    """ processing loop. Loop continuosly. Keep track of the time, when the wakeup
        time comes around set off the lights. Every 6 hours query the time NTP server
        and update the microcontrollers clock.
    Arguments:
        strip - neopixel object
    Local Variables:
        hourMin - the current hour and minute
    Returns:
        Nothing """
    while True:
        #Keep track of the time.
        hourMin = getLocalTime()[3:5]
        #when we hit the wakeup time setup and run the lights task
        if hourMin == WAKEUP_TUPLE:
            await lights(strip)
        #Every 6 hours query the time server and reconcile the NTP time with the
        # ESP32 Real Time Clock
        if hourMin == (0, 0) or hourMin == (6, 0) or hourMin == (12, 0) or hourMin == (18, 0):
            updateRTCFromNTP(strip)
    
async def lights(strip):
    """ Fade up the lights, wait at full brightness, then fade down
    Arguments:
        strip - neopixel object
    Local Variables:
        None
    Returns:
        Nothing """
    clearStrip(strip)
    fade(LED_COLOR_OFF, LED_COLOR_FULL, 60, 0.02, strip)
    utime.sleep(LIT_LENGTH * SEC_IN_HOUR)
    fade(LED_COLOR_FULL, LED_COLOR_OFF, 60, 0.02, strip)
    clearStrip(strip)
    
def fade(startColor, endColor, steps, interval, strip):
    """ Fade up the lights, wait at full brightness, then fade down
    Arguments:
        startColor - Starting RGB values for neopixel strip
        endColor - Ending RGB values for neopixel strip
        steps - number of steps to take between startColor and endColor
        interval - time to wait between steps in seconds.
        strip - neopixel object
    Local Variables:
        i - counter
        red - red values
        green - green values
        blue - blue Values
        lastUpdate -  the last time the neopixel strip was updated
    Returns:
        Nothing """
    lastUpdate = utime.time() - interval
    for i in range(0, steps):
        red = ((startColor[0] * (steps - i)) + (endColor[0] * i)) // steps
        green = ((startColor[1] * (steps - i)) + (endColor[1] * i)) // steps
        blue = ((startColor[2] * (steps - i)) + (endColor[2] * i)) // steps
        
        while ((utime.time() - lastUpdate) < interval):
            pass
        setStrip(strip, (red, green, blue))
        lastUpdate = utime.time()
                
def main():
    """ Setup neopixel object, run setup function and start the processing loop (clock)
    Arguments:
        None
    Local Variables:
        led - Pin object
    Returns:
        Nothing """
    LEDStrip = createNeoPixelObject()
    uasyncio.run(setup(LEDStrip))
    uasyncio.run(clock(LEDStrip))
    
if __name__ == '__main__':
    main()
    
