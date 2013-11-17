#!/bin/sh
cd $(dirname $(readlink -f $0))
. bin/activate



while sleep 1;do
        python hal.py
        echo "!! HAL crashed, restarting"
done
