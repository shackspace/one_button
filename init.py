#!/usr/bin/env python
from threading import Timer,Thread
import RPIO
from RPIO import PWM
import paramiko
import json
import sys
from time import time, sleep
from relaxxapi.relaxxapi import relaxx
r = None
sftp_base_path = "/home/shack/music"


button = 4
loud1 = 21
loud2 = 22
light = 17
hal_speed=15

state = 0


def init_state():
    state = 0
    RPIO.setwarnings(False)
    RPIO.setup(loud1, RPIO.OUT)
    RPIO.setup(loud2, RPIO.OUT)

def start_hal(speed):
    PWM.setup()
    PWM.init_channel(0 )
    PWM.set_loglevel(PWM.LOG_LEVEL_ERRORS)
    current = lower = 300
    up = True
    upper = 1800
    step = 50
    while 1:
        PWM.add_channel_pulse(0,light,0,current)
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
        sleep(1.0/speed)
     

t1_2 = 1
timer1=None
t2_4 = 1
timer2=None
t4_5 = 3
timer3=None

def time3_trans():
    global state
    if state is 4:
        state = 5
        stop_sirene1()
        stop_sirene2()
    else:
        print("State is not 4, will do nothing")


def time2_trans():
    global state
    global timer3
    if state is 2:
        state = 4
        start_sirene2()
        timer3= Timer(t4_5,time3_trans).start()
    else:
        print("State is not 2, will do nothing")

def time1_trans():
    global state
    global timer2
    if state is 1:
        state = 2
        start_sirene1()
        timer2=Timer(t2_4,time2_trans).start()
    else:
        print("State is not 1, will do nothing")


def btn_trans(a,edge):
    global state
    global timer1
    print("Button: %s , edge: %s, state: %d" % (str(a), str(edge),state))
    if edge and state is 0:
        state = 1
        timer1=Timer(t1_2,time1_trans).start()
    # stopped pressing the button but the timeout is not over
    elif not edge and (state is 1 or state is 4):
        state = 0
        disable_all_timers()
        stop_sirene1()
        stop_sirene2()
        play_next()
    elif not edge and state is 5:
        state = 0
        disable_all_timers()
        delete_current_music()
        
        
def disable_all_timers():
    print("disabling all the timers")
    global timer1
    global timer2
    global timer3
    try:
        timer1.cancel()
        print("timer1 canceled")
    except: pass
    try:
        timer2.cancel()
        print("timer2 canceled")
    except: pass
    try:
        timer3.cancel()
        print("timer3 canceled")
    except: pass

def start_sirene1(): 
    print("start Sirene 1")
    RPIO.output(loud1, True)

def start_sirene2(): 
    print("starting Sirene 2")
    RPIO.output(loud2, True)

def stop_sirene1(): 
    print("stopping Sirene 1")
    RPIO.output(loud1, False)

def stop_sirene2(): 
    print("stopping Sirene 2")
    RPIO.output(loud2, False)

def play_radio():
    #TODO play radio
    if r.get_current().get("file", "") == "http://ice.somafm.com/groovesalad":
        print("will not skip own sender")
        return
    print("playing radio")
    r.add_song("http://ice.somafm.com/groovesalad")
    r.play_last()


def play_next():
    print ("playing next song")
    try:
        #sanity
        if is_last_song():
            raise Exception("Last song in playlist")
        r.next_song()
    except:
        print("no next song, starting radio")
        play_radio()

def is_last_song():
    return r.get_current()["Pos"] == r.get_last()["Pos"]



def delete_current_music():
    print("delete current music")
    current = r.get_current()
    if not current:
        print("Nothing is running, bailing out")
        return
    delete_remote_file(current)
    play_next()


def delete_remote_file(current):
    try:
        sftp_delete_remote_file(current["file"])
        tell_gobbelz(current.get("Title", "Unbekannter Title"),
                     current.get("Artist", "Unbekannter Kuenstler"))
    except :
        print("Cannot delete remote file!")


def sftp_delete_remote_file(f):
    host = "mpd.shack"
    port = 22
    transport = paramiko.Transport((host, port))
    username = 'shack'
    passwd = 'shackit'
    transport.connect(username=username, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport)
    #print(sftp.stat('%s/%s'%(base_path,f)))
    print(sftp.unlink('%s/%s' % (sftp_base_path, f)))
    sftp.close()
    transport.close()

def tell_gobbelz(name, author):
    import requests
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'text': '%s von %s wurde vernichtet!' % (name, author)}
    #  curl -i -H "content-type: application/json"
    #     -X POST -d "{\"text\" : \"Hallo shackspace\"}" kiosk.shack:8080/say/
    requests.post("http://kiosk.shack:8080/say/",
                  data=json.dumps(data), headers=headers)


if __name__ == "__main__":
    from time import sleep
    #BCM layout
    #Board layout
    #channel=11
    init_state() 
    print("Starting HAL")
#t.start()
    print("initializing relaxxapi")
    r = relaxx(relaxxurl="http://lounge.mpd.shack/")
    print("adding interrupt")
    RPIO.add_interrupt_callback(button,callback=btn_trans,pull_up_down=RPIO.PUD_DOWN,threaded_callback=True) #,debounce_timeout_ms=1
    print ("Waiting...")
    RPIO.wait_for_interrupts(threaded=True)
    #Thread(target=start_hal,args=(hal_speed,)).start()
    while True:
        start_hal(hal_speed)
