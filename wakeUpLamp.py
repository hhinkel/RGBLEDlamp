import machine
import sys
import network
import utime
import ntptime
import uasyncio
import neopixel

#User constants
SSID = 'Your SSID'
PW = 'Network Password'
TIME_ZONE = -5   #hours from GMT. This is EST
LIT_LENGTH = 3600 #Seconds at brightest setting 
WAKEUP_TUPLE = (04, 45)  #time lights come on in 24hr format, hour and minute
PIN = 27
NUM_NEOPIXELS = 60

LIGHTS_ON = False

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

async def setup(strip):
    #Test the LEDs
    lightDemo(strip)
    #Set the clock for the first time
    updateRTCFromNTP()
    return getWakeupTime()

def lightDemo(strip):
    setStrip(strip,(255, 255, 255))
    utime.sleep(0.5)
    clearStrip(strip)

def clearStrip(strip):
    strip.fill((0, 0, 0))
    strip.write()
     
def setStrip(strip,temp):
    strip.fill(temp)
    strip.write()

def updateRTCFromNTP():
    wifi = connectToWifi()
    print("GMT time before synchronization：%s" %str(utime.localtime()))
    try:
        ntptime.settime()
    except OSError:
        print("Can not connect to NTP server")
        machine.reset()
    localTime = getLocalTime() 
    print("GMT time after synchronization：%s" %str(utime.localtime()))
    print("Local time after synchronization：%s" %str(localTime))
    disconnectFromWifi(wifi)

def connectToWifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID,PW)
    while not wifi.isconnected():
        pass
    return wifi

def disconnectFromWifi(wifi):
    wifi.disconnect()
    wifi.active(False)

def getLocalTime():
    return (utime.localtime(utime.time() + TIME_ZONE * 3600))

async def getWakeupTime():
    return getLocalTime()[0:3] + WAKEUP_TUPLE + getLocalTime()[5:]

def createNeoPixelObject():
    return neopixel.NeoPixel(machine.Pin(PIN), NUM_NEOPIXELS)

async def clock(wakeupTime, strip):
    while True:
        #Keep track of the time.
        hourMin = getLocalTime()[3:5]
        #when we hit the wakeup time setup and run the lights task
        if hourMin == WAKEUP_TUPLE:
            await lights(strip)
        #Every 6 hours query the time server and reconcile the NTP time with the
        # ESP32 Real Time Clock
        if hourMin == (0, 0) or hourMin == (6, 0) or hourMin == (12, 0) or hourMin == (18, 0):
            updateRTCFromNTP()
    
async def lights(strip):
    clearStrip(strip)
    fade((0,0,0), (255,255,255), 60, 0.02, strip)
    utime.sleep(LIT_LENGTH)
    fade((255,255,255), (0,0,0), 60, 0.02, strip)
    clearStrip(strip)
    
def fade(startColor, endColor, steps, interval, strip):
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
    LEDStrip = createNeoPixelObject()
    wakeupTime = uasyncio.run(setup(LEDStrip))
    uasyncio.run(clock(wakeupTime, LEDStrip))
    
if __name__ == '__main__':
    main()
    
