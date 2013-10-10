#!/usr/bin/env python
import json
from relaxxapi.relaxxapi import relaxx
r = relaxx()
current = r.get_current()
#print(json.dumps(current))
print("ssh shack@mpd.shack 'rm \"music/%s\"'" % current["file"])
