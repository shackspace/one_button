#!/bin/sh
cd $(dirname $(readlink -f $0))
. bin/activate
while sleep 1;do
        python init.py
done
