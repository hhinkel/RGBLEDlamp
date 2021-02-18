import machine
import sys
import network
import utime
import ntptime
import uasyncio
import neopixel

#User constants
SSID = 'SSID'
PW = 'Password'
TIME_ZONE = -5   #hours from GMT. This is EST
WAKEUP_TUPLE = (20, 40)  #time lights come on in 24hr format, hour and minute
PIN = 27
NUM_NEOPIXELS = 144

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

def getZoneTime():
    return (utime.localtime(utime.time() + TIME_ZONE * 3600))

def determineWakeupTime():
    return getZoneTime()[0:3] + WAKEUP_TUPLE + getZoneTime()[5:]

def updateRTCFromNTP():
    wifi = connectToWifi()
    print("GMT time before synchronization：%s" %str(utime.localtime()))
    try:
        ntptime.settime()
    except OSError:
        print("Can not connect to NTP server")
        machine.reset()
    localZoneTime = getZoneTime() 
    print("GMT time after synchronization：%s" %str(utime.localtime()))
    print("Local time after synchronization：%s" %str(localZoneTime))
    disconnectFromWifi(wifi)

def startLightSequence():
    strip = createNeoPixelObject()
    setStrip(strip,(0, 0, 255))
    utime.sleep(1)
    clearStrip(strip)

def createNeoPixelObject():
    return neopixel.NeoPixel(machine.Pin(PIN), NUM_NEOPIXELS)

def clearStrip(strip):
    strip.fill((0, 0, 0))
    strip.write()
    
def setStrip(strip,temp):
    strip.fill(temp)
    strip.write()

def main():
    #This is setup
    updateRTCFromNTP()
    alarm = determineWakeupTime()
    print(alarm)
    
    #this is the loop
    while True:
        hourMin = getZoneTime()[3:5]
        print(hourMin)
        #If local midnight reset local time and the alarm tuple
        if hourMin == (0, 0):
            updateRTCFromNTP()
            date = getZoneTime()[0:4]
            alarm = determineWakeupTime()
            print(alarm)
        if hourMin == WAKEUP_TUPLE:
            #async?
            startLightSequence()
        utime.sleep(30)
    
if __name__ == '__main__':
    main()
