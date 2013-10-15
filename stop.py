#!/usr/bin/python

import RPIO
from time import sleep
pin=17
pin2=21
pin3=22
RPIO.setup(pin, RPIO.OUT)
RPIO.setup(pin2, RPIO.OUT)
RPIO.setup(pin3, RPIO.OUT)
toggle = False
RPIO.output(pin, toggle)
RPIO.output(pin2, toggle)
RPIO.output(pin3, toggle)
