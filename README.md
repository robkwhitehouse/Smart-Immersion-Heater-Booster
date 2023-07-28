# Smart-Immersion-Heater-Booster
Smart Hot Water booster.
A small python program to initiate an immersion heater boost period.
The boost period is dynamically adjusted according to the current charge state of my  domestic battery
The idea is that it will use surplus battery charge only (no grid power)
My domestic battery is charged during the day by solar panels only (but yours might not be)

This program is fairly specific to my own solar power installation. This consists of
* A Givenergy 5KW Inverter
* A Givenergy Battery (5.2KWh)
* A Myenergi EDDI immersion controller

It makes use of the cloud APIs that are exposed by Myenergi and Givenergy for their products and
is (I think) a useful example of how to use those APIs

I run this program on a Raspberry Pi Zero W which is running the standard Pi OS (i.e. Debian Linux)
but it could be run on anthing that has a python interpreter and an internet connection.

I run this program at 06:00 every day using cron. It provides me with free hotwater in the morning.
The crontab entry is;
00 06 * * * python $HOME/HotWater.py

But it can be invoked manually or however you want

It creates (or overwrites) a new log file every time in the working directory called HotWater.log
The log file will tell you what the program did (or didn't do) and any errors and warnings

**N.B. YOU MUST EDIT THE PYTHON FILE AND CHANGE THE API KEYS AND SERIAL NUMBERS 
THESE ARE DEFINED AS CONSTANTS AT THE TOP OF THE FILE**

