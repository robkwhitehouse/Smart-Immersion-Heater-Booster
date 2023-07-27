#! python

# Activate EDDI immersion heater Boost for a number of minutes
# The number of minutes is calculated from the solar battery charge state
# I.e. the intention is that only surplus battery charge is used for this purpose
# Surplus is defined as anything more than 25%, i.e. always keep 25% in reserve
# This is configurable (see below)

# It is intended that this script will be run by cron at 06.00am each day
# It generates a new log file called HotWater.py in the current
# working directory each time it is run. This avoids logfile housekeeping

# But it can be run manually at anytime to kick of a smart HW boost

# It uses cloud APIs that are exposed by Givenergy (for the battery charge state)
# and Myenergi (to activate the EDDI manual boost feature)

###
# You MUST edit and change the following constants;
###
#
# GivEnergy API site specific constants - will need to be changed

GE_INVERTER_SN = 'FD2311G675'
GE_API_KEY = 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiI5NTc3MDIxOS1jYWE2LTRmOTctOTE3Ni0zNDBlZGMzZDQxNTgiLCJqdGkiOiIwYTFlNzI1NTA4NmUxMGQ3MWRhZjE1OWQxZTY2MTU1MGMyYTlkMDBiMjBlMTZlYWJmMWNiZTA1NmVhYjBlMDQ1OTQ3NDNhM2RhNTFiNWRlYiIsImlhdCI6MTY4OTYwNDEwMi45MDY2NzYsIm5iZiI6MTY4OTYwNDEwMi45MDY2ODEsImV4cCI6MTcyMTIyNjUwMi44OTk5MDgsInN1YiI6IjQxNTcwIiwic2NvcGVzIjpbImFwaSJdfQ.MCceGVluN1wVj1wwx50LobAdwP5PkuIjT11-ppnpVYFV7gsbcuMa7V5ISk99SF_QoMtkeJsjQZganyWtNzckgQ'

# Myenergi site specific constants - will need to be changed

EDDI_SERIAL = '21445826'
ME_API_KEY = 'Dnht2ZfEJXdf5FPIuPJbifJ3'
ME_SERVER = 's18'

#
#Some or all of the following paramaters will probably also need to be tweaked
#To suit personal preferences and/or local installation specifics 

BATTERY_RESERVE = 25 #percent - don't do any boosting if battery charge is below this
MAX_TIME = 40 #minutes - no point in using anything more - tank will be max temp
EDDI_BOOST_CURRENT = 9 #amps - this defaults to 13A but should be limited (by EDDI settings) to ensure that max battery current is never exceeded.
BATTERY_CAPACITY = 5000 #Watt hours
MAINS_VOLTAGE = 240 #volts (UK)

#You shouldn't need to change much below here

#Python Modules
import requests #http requests library
from requests.auth import HTTPDigestAuth #required ny myenergi API
import json
import logging
#import os


#The log file will be overwritten each time this program starts (every day) - avoids housekeeping
logging.basicConfig(filename='HotWater.log', filemode='w', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logging.info('HotWater.py starting')

#
# Uses GivEnergy cloud API to retrieve battery charge (percentage)

# Build GE API URL
GE_API_URL = 'https://api.givenergy.cloud/v1/inverter/{}/system-data/latest'.format(GE_INVERTER_SN)
payload = "{'inverter_serials': [GE_INVERTER_SN], 'setting_id': 17}"
headers = {
'Authorization': GE_API_KEY,
'Content-Type' : 'application/json',
'Accept' : 'application/json'
}

def MyEnergyBatteryCharge():
    response = requests.get(GE_API_URL, data = payload, headers = headers)
    if (response.status_code != 200):
        logging.error(f'GiveEnergy API call failed. Status {reponse.status_code} returned.')
        exit(1)
    response_json = response.json()
    return response_json['data']['battery']['percent'] 

#
# Uses the myEnergy API to start a hot water boost for the given number of minutes
# MyEnergi EDDI site specific constants - will need to be changed
#
# Does not return anything

EDDI_BOOST_POWER = EDDI_BOOST_CURRENT * MAINS_VOLTAGE #Watts     
def EDDIBoost(minutes):
    if (minutes > MAX_TIME):
        minutes = MAX_TIME
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    EDDI_url  = 'https://' + ME_SERVER + '.myenergi.net/cgi-eddi-boost-E' + EDDI_SERIAL + f"-10-1-{minutes}"
    response = requests.get(EDDI_url, auth=HTTPDigestAuth(EDDI_SERIAL,ME_API_KEY), headers=headers, timeout=20)

    if (response.status_code != 200):
       response_json = response.json()
       logging.error(response_json)
       exit(1)
# End of EDDIBoost()


###
# Main logic entry point - execution starts here (sort of)
###

#First check that we have a WiFi or other LAN connection
## TODO - not working
#response = os.system("ping -c1 -w2 192.168.1.254")
#if (response != 0):
#    logging.error("No LAN connection. Aborting.")
#    exit(1)

batteryCurrentCharge = MyEnergyBatteryCharge() # Call the ME cloud API to get battery charge (%)
batterySurplusPercent = batteryCurrentCharge - BATTERY_RESERVE
#Now convert surplus charge (percentage of battery max) into boost minutes
batterySurplusCharge = batterySurplusPercent * BATTERY_CAPACITY / 100 #Gives surplus charge in watt hours
boostMinutes = round(batterySurplusCharge / EDDI_BOOST_POWER * 60)    #(60 minutes in an hour)

if batterySurplusCharge > 0:
    if boostMinutes > MAX_TIME:
        boostMinutes = MAX_TIME   
    EDDIBoost(boostMinutes) #kick off the immersion boost
    logging.info('*** EDDI manual boost started ***')
    logging.info(f'Battery charge = {batteryCurrentCharge}%')
    logging.info(f'Battery surplus = {batterySurplusCharge} Watt hours')
    logging.info(f'Boost period = {minutes} minutes')
else:
    logging.warning(f'Battery charge = {batteryCurrentCharge}%')
    logging.warning('No surplus charge, boost not started')

#exit(0)   

