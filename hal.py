from RPIO import PWM
from time import sleep
PWM.setup()

current = lower = 300
up = True
upper = 1600
step = 30
PWM.init_channel(0)
hal_led = 17
hal_speed=15
PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
print("Starting hal fade")
while 1:
    PWM.add_channel_pulse(0,hal_led,0,current)
    if up:
        if (current + step) < upper:
            current = current + step
        else:
            print("Fading down")
            up = not up
    else:
        if (current - step) > lower:
            current = current - step
        else:
            print("Fading up")
            up = not up
    sleep(1.0/hal_speed)
