#!/usr/bin/env python
import json
from relaxxapi.relaxxapi import relaxx
r = relaxx()
print(json.dumps(r.get_current()))
