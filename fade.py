from RPIO import PWM
from time import sleep
PWM.setup()

current = lower = 300
up = True
upper = 1600
step = 30
PWM.init_channel(0)

while 1:
    PWM.add_channel_pulse(0,17,0,current)
    PWM.add_channel_pulse(0,27,0,current)
    PWM.add_channel_pulse(0,22,0,current)
    if up:
        if (current + step) < upper:
            current = current + step
        else:
            up = not up
    else:
        if (current - step) > lower:
            current = current - step
        else:
            up = not up
    sleep(0.05)
