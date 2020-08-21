#!/usr/bin/python
# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import time
import signal
import sys
import os

# Configuration
FAN_PIN = 18            # BCM pin used to drive PWM fan
WAIT_TIME = 1           # [s] Time to wait between each refresh
PWM_FREQ = 25000        # [Hz] 25kHz for Noctua PWM control

# Configurable temperature and fan speed
MIN_TEMP = 45
MAX_TEMP = 70
FAN_LOW = 40
FAN_HIGH = 100
FAN_OFF = 0
FAN_MAX = 100
FAN_ON = False
TEMP_DIFF = 10

# Get CPU's temperature
def getCpuTemperature():
    res = os.popen('vcgencmd measure_temp').readline()
    temp =(res.replace("temp=","").replace("'C\n",""))
    #print("temp is {0}".format(temp)) # Uncomment for testing
    return temp

# Set fan speed
def setFanSpeed(speed):
    fan.start(speed)
    return()

# Handle fan speed
def handleFanSpeed(FAN_ON):
    temp = float(getCpuTemperature())
    # Turn off the fan if temperature is TEMP_DIFF degrees below MIN_TEMP
    if temp < MIN_TEMP:
        if (temp < (MIN_TEMP - TEMP_DIFF)) and (FAN_ON):
            setFanSpeed(FAN_OFF)
            FAN_ON = False
            #print("Fan OFF") # Uncomment for testing
        else:
            return(FAN_ON)
    # Set fan speed to MAXIMUM if the temperature is above MAX_TEMP
    elif temp > MAX_TEMP:
        setFanSpeed(FAN_MAX)
        FAN_ON = True
        #print("Fan MAX") # Uncomment for testing
    # Caculate dynamic fan speed
    else:
        step = (FAN_HIGH - FAN_LOW)/(MAX_TEMP - MIN_TEMP)   
        temp -= MIN_TEMP
        setFanSpeed(FAN_LOW + ( round(temp) * step ))
        FAN_ON = True
        #print(FAN_LOW + ( round(temp) * step )) # Uncomment for testing
    return(FAN_ON)

try:
    # Setup GPIO pin
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT, initial=GPIO.LOW)
    fan = GPIO.PWM(FAN_PIN,PWM_FREQ)
    setFanSpeed(FAN_OFF)
    # Handle fan speed every WAIT_TIME sec
    while True:
        FAN_ON = handleFanSpeed(FAN_ON)
        time.sleep(WAIT_TIME)

except KeyboardInterrupt: # trap a CTRL+C keyboard interrupt
    setFanSpeed(FAN_HIGH)
    #GPIO.cleanup() # resets all GPIO ports used by this function