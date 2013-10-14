#!/usr/bin/env python
import paramiko
import json,sys
from relaxxapi.relaxxapi import relaxx
r = None

def delete_current_music(a,b):
    print("balls")
    current = r.get_current()
    #print(json.dumps(current))
    base_path="/home/shack/music"
    
    
    if not current:
        print("Nothing is running, bailing out")
        return
    #print(json.dumps( current))
    #print("ssh shack@mpd.shack 'rm \"music/%s\"'" % current["file"])
    delete_remote_file(current["file"])

def delete_remote_file(f):
    host = "mpd.shack"
    port = 22
    transport = paramiko.Transport((host, port))
    username = 'shack'
    passwd= 'shackit'
    transport.connect(username = username,password=passwd)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print(sftp.stat('%s/%s'%(base_path,f)))
    #print(sftp.unlink('%s/%s'%(base_path,f)))
    sftp.close()
    transport.close()


if __name__ == "__main__":
    import RPIO
    channel=11
    #RPIO.setmode(RPIO.BOARD)
    RPIO.setup(channel, RPIO.IN)
     
    print("initializing relaxxapi")
    r = relaxx()
    print("adding interrupt")
    RPIO.add_interrupt_callback(channel,delete_current_music,debounce_timeout_ms=10,threaded_callback=True)
    print ("Waiting...")
    RPIO.wait_for_interrupts()
