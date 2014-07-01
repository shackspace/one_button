#!/usr/bin/env python
from threading import Timer,Thread
import RPIO
from RPIO import PWM
import paramiko
import json
import sys
from time import time, sleep

from mpd import MPDClient
r = None
state = 0

# original mpd
sftp_base_path = "/home/shack/music"
mpd_host = "mpd.shack"
# lounge port
mpd_port = 6600
ssh_host = "mpd.shack"

# tmpd
sftp_base_path = "/home/shack/music"
mpd_host = "tmpd.shack"
ssh_host = "tmpd.shack"
mpd_port = 6600




gobbelz_uri="http://kiosk.retiolum:8080/say/"
ssh_user = "shack"
ssh_pass = "shackit"
button = 24
loud1 = 21
loud2 = 22
stream_uri = "http://ice.somafm.com/groovesalad"

# sftp_base_path = "/var/lib/mpd/music/"
# gobbelz_uri="http://localhost/"
# mpd_host = "localhost"
# ssh_host = "localhost"
# ssh_user = "pi"
# ssh_pass = "not pi"
# loud1 = 1
# loud2 = 2





def init_audio():
    global r
    tprint("init audio")
    try:
        if not r.ping():
            tprint("disconnecting mpd")
            r.disconnect()
            r.connect(mpd_host,mpd_port)
        else:
            tprint("all fine with mpd connector") 
    except:
        tprint("failed hard while connecting")
        r = MPDClient()
        r. timeout = 10
        r.idletimeout = None
        r.connect(mpd_host,mpd_port)
    return r

def init_state():
    state = 0
    RPIO.setup(loud1, RPIO.OUT)
    RPIO.setup(loud2, RPIO.OUT)


def tprint(fmt):
        print(str(time()) +" "+fmt)

t1_2 = 1
timer=None
t2_4 = 1
t4_5 = 3

def time3_trans():
    global state
    if state is 4:
        state = 5
        stop_sirene1()
        stop_sirene2()
        disable_all_timers()
        delete_current_music()
        state = 0
    else:
        tprint("State is not 4, will do nothing")


def time2_trans():
    global state
    global timer
    if state is 2:
        state = 4
        start_sirene2()
        timer= Timer(t4_5,time3_trans)
        timer.start()
    else:
        tprint("State is not 2, will do nothing")

def time1_trans():
    global state
    global timer
    tprint("Reached time1 transition")
    if state is 1:
        tprint("State is 1")
        state = 2
        start_sirene1()
        timer=Timer(t2_4,time2_trans)
        timer.start()
    else:
        tprint("State is not 1, stopping everything")


def btn_trans(a,edge):
    global state
    global timer
    if not edge and state is 0:
        tprint("Ignoring retard state")
        return
    tprint("Button: %s , edge: %s, state: %d" % (str(a), str(edge),state))
    if edge and state is 0:
        state = 1
        if not timer:
            timer=Timer(t1_2,time1_trans)
            timer.start()
        else:
            tprint("Timer is already running. this should never happen")
            disable_all_timers()
            stop_sirene1()
            stop_sirene2()
    # stopped pressing the button but the timeout is not over
    elif not edge and (state is 1 or state is 4 or state is 2):
        state = 0
        disable_all_timers()
        stop_sirene1()
        stop_sirene2()
        try:
            play_next()
        except:
            tell_gobbelz("Cannot play next song. Restarting")
            tell_gobbelz("Please press the button again in ten seconds.")
            sys.exit(1)
            
    elif not edge and state is 5:
        tprint("button released while removing music, all fine")
    else:
        tprint("this should never happen.stopping everything")
        tell_gobbelz("Stop playing around with the one button!") 
        disable_all_timers()
        stop_sirene1()
        stop_sirene2()
        
        
def disable_all_timers():
    tprint("disabling all the timers")
    global timer
    try:
        timer.cancel()
        tprint("timer canceled")
    except Exception as e:
        tprint("cannot cancel timer! %s" %str(e))
    timer = None

def start_sirene1(): 
    tprint("start Sirene 1")
    RPIO.output(loud1, True)

def start_sirene2(): 
    tprint("starting Sirene 2")
    RPIO.output(loud2, True)

def stop_sirene1(): 
    tprint("stopping Sirene 1")
    RPIO.output(loud1, False)

def stop_sirene2(): 
    tprint("stopping Sirene 2")
    RPIO.output(loud2, False)

def play_radio():
    #TODO play radio

    if r.currentsong().get("file", "") == stream_uri:
        tprint("will not skip own sender")
        tell_gobbelz("Radio Stream is already running")
        return
    tprint("playing radio")
    tell_gobbelz("Starting Radio Stream")
    r.add(stream_uri)
    r.play(r.playlistinfo()[-1]["pos"])

    

def play_next():
    r = init_audio() 
    tprint ("playing next song")
    try:
        #sanity
        if is_last_song():
            raise Exception("Last song in playlist")
        r.next()
    except:
        tprint("no next song, starting radio")
        play_radio()

def is_last_song():
    r = init_audio() 
    return r.currentsong()["pos"] == r.playlistinfo()[-1]["pos"]

def delete_current_music():
    r = init_audio() 
    tprint("delete current music")
    current = r.currentsong()
    if not current:
        tprint("Nothing is running, bailing out")
        tell_gobbelz("Nothing is running, cannot delete")
        return
    delete_remote_file(current)
    try:
        tprint("deleting the currently running song which should be gone now")
        r.delete(r.currentsong()['pos'])
        if not r.currentsong():
            tprint("no song playing, starting radio")
            play_radio()
    except:
        tprint("playing the nxt song")


def delete_remote_file(current):
    try:
        sftp_delete_remote_file(current["file"])
        say_song_killed(current.get("title", "Unnamed Title"),
                     current.get("artist", "Unnamed Author"))
    except Exception as e:
        #from pdb import set_trace; set_trace()
        tprint("Cannot delete remote file! ( %s ) " %str(e))
        import traceback
        print(traceback.format_exc())
        tell_gobbelz("Cannot delete the song '%s' from EM PE DEE" % current.get("title", "Unnamed Title"))


def sftp_delete_remote_file(f):
    host = ssh_host
    port = 22
    transport = paramiko.Transport((host, port))
    username = ssh_user
    passwd = ssh_pass
    transport.connect(username=username, password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport)
    #print(sftp.stat('%s/%s'%(base_path,f)))
    sftp.unlink('%s/%s' % (sftp_base_path, f))
    tprint( "removing %s/%s" % (sftp_base_path, f))
    sftp.close()
    transport.close()

def say_song_killed(name, author):
    tell_gobbelz('%s by %s was destroyed!' % (name, author) )

def tell_gobbelz(text):
    import requests
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    data = {'text': text}
    tprint("Saying gobbelz: %s"% text)
    #  curl -i -H "content-type: application/json"
    #     -X POST -d "{\"text\" : \"Hallo shackspace\"}" kiosk.shack:8080/say/
    try:
        requests.post(gobbelz_uri,
                  data=json.dumps(data), headers=headers,timeout=10)
    except Exception as e:
	print(e)
        tprint("gobbelz failed")


if __name__ == "__main__":
    from time import sleep
    init_state() 
    tprint("adding interrupt")
    RPIO.add_interrupt_callback(button,callback=btn_trans,pull_up_down=RPIO.PUD_DOWN ,debounce_timeout_ms=1)
    #RPIO.add_interrupt_callback(button,callback=btn_trans,pull_up_down=RPIO.PUD_UP)
    tprint ("Start Interrupt handler")
    RPIO.wait_for_interrupts()
