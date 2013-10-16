#!/usr/bin/env python
import json,sys
from relaxxapi.relaxxapi import relaxx
r = relaxx()
current = r.get_current()
#print(json.dumps(current))
base_path="/home/shack/music"


if not current:
    print("Nothing is running, bailing out")
    sys.exit(0)
print(json.dumps( current))
print("ssh shack@mpd.shack 'rm \"music/%s\"'" % current["file"])


host = "mpd.shack"
port = 22
transport = paramiko.Transport((host, port))
username = 'shack'
passwd= 'shackit'
transport.connect(username = username,password=passwd)
sftp = paramiko.SFTPClient.from_transport(transport)
print(sftp.stat('%s/%s'%(base_path,current["file"])))
#print(sftp.unlink('%s/%s'%(base_path,current["file"])))
sftp.close()
transport.close()
