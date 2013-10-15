#!/usr/bin/env python
from threading import Timer
import RPIO
from RPIO import PWM
import paramiko
import json,sys
from time import time
from relaxxapi.relaxxapi import relaxx
r = None
base_path="/home/shack/music"
state=0
# state 0 
#       low :do nothing
#       high:begin timing, goto state 1
# 
# timer sets state to 2 if state is still 1
# 
# state 1 
#       low : reset timer, goto state 0
#       high:do nothing (should not happen)
# state 2:
#       low : reset timer,
# 
# not current = off
# current = on
timer=0
TIMEOUT=5
#radio_list= [


button=17
loud1=14
loud2=15
light=18

def pwm_light():
    


def init_state():
    PWM.setup()
    PWM.init_channel(0,1000)
    PWM.add_channel_pulse(0,light,start=0,width=
    state=0

def tell_gobbelz(name,author):
    import requests
    import json
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = { 'text': '%s von %s wurde vernichtet!'%(name,author)}
    #   curl -i -H "content-type: application/json" -X POST -d "{\"text\" : \"Hallo shackspace\"}" kiosk.shack:8080/say/
    requests.post("http://kiosk.shack:8080/say/",data=json.dumps(data),headers=headers)
    
  
def play_radio():
    #TODO play radio
    if r.get_current().get("file","") == "http://ice.somafm.com/groovesalad": 
        print("will not skip own sender")
        return
    print("playing radio")
    r.add_song("http://ice.somafm.com/groovesalad")
    r.play_last()

def is_last_song():
    return r.get_current()["Pos"] == r.get_last()["Pos"]

def rising_state(a,edge):
    print("Button: %s , edge: %s"%(str(a),str(edge)))
    return 
    global state
    global timer
    global TIMEOUT
    global r
    if state == 0:
        if edge:
            timer=time()
            print("Button pressed at %d"%timer)
            state = 1
    # less than 2 seconds
    elif state == 1:
        if not edge:
            if ( time()-timer) < TIMEOUT :
                print("timeout not reached (%d seconds of %d)\nplaying next song"% (time()-timer,TIMEOUT))
                try:
                    #sanity if the list is not empty, bail out
                    if is_last_song(): raise Exception("Last song in playlist")
                    # try to run next_song, this will always work...
                    r.next_song()

                except:
                    print("no next song, starting radio")
                    play_radio()

                    #print("no next song, clearing")

                    #r.stop()
                    #r.clear()
                state = 0
            else:
	        state = 2
    if state == 2:
        print("Will Delete File (timer %d seconds)"% (time()-timer))
        delete_current_music()
        state = 0
        

def delete_current_music():
    current = r.get_current()
    print(json.dumps(current))
    if not current:
        print("Nothing is running, bailing out")
        return
    try:
        delete_remote_file(current["file"])
        tell_gobbelz(current.get("Title","Unbekannter Title"),current.get("Artist","Unbekannter Kuenstler"))
    except:
        print("Cannot delete remote file!")

    try:
        #sanity
	if is_last_song(): raise Exception("Last song in playlist")
        r.next_song()
    except:
	print("no next song, starting radio")
        play_radio()

def delete_remote_file(f):
    host = "mpd.shack"
    port = 22
    transport = paramiko.Transport((host, port))
    username = 'shack'
    passwd= 'shackit'
    transport.connect(username = username,password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport)
    #print(sftp.stat('%s/%s'%(base_path,f)))
    print(sftp.unlink('%s/%s'%(base_path,f)))
    sftp.close()
    transport.close()


if __name__ == "__main__":
    from time import sleep
    #BCM layout
    #Board layout
    #channel=11
    init_state() 
    print("initializing relaxxapi")
    r = relaxx(relaxxurl="http://lounge.mpd.shack/")
    print("adding interrupt")
    RPIO.add_interrupt_callback(button,callback=rising_state ,pull_up_down=RPIO.PUD_DOWN) #,debounce_timeout_ms=1
    print ("Waiting...")
    RPIO.wait_for_interrupts()
