#!/usr/bin/env python
from threading import Timer
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
loud1 = 18
loud2 = 21
light = 22

state = 0


def init_state():
    PWM.setup()
    PWM.init_channel(0, 1000)
    state = 0


def tell_gobbelz(name, author):
    import requests
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'text': '%s von %s wurde vernichtet!' % (name, author)}
    #  curl -i -H "content-type: application/json"
    #     -X POST -d "{\"text\" : \"Hallo shackspace\"}" kiosk.shack:8080/say/
    requests.post("http://kiosk.shack:8080/say/",
                  data=json.dumps(data), headers=headers)
 

def play_radio():
    #TODO play radio
    if r.get_current().get("file", "") == "http://ice.somafm.com/groovesalad":
        print("will not skip own sender")
        return
    print("playing radio")
    r.add_song("http://ice.somafm.com/groovesalad")
    r.play_last()


def play_next():
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


def btn_transition(a,edge):
    print("Button: %s , edge: %s" % (str(a), str(edge)))


def delete_current_music():
    current = r.get_current()
    print(json.dumps(current))
    if not current:
        print("Nothing is running, bailing out")
        return
    delete_remote_file(current)


def delete_remote_file(current):
    try:
        sftp_delete_remote_file(current["file"])
        tell_gobbelz(current.get("Title", "Unbekannter Title"),
                     current.get("Artist", "Unbekannter Kuenstler"))
    except:
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
