#!/bin/bash
# a simple script to open the content and frontend servers (convienience script)

#obtain ports
ports=`python config.py`
set -- $ports
ai=$1
ap=$2

python server/manage.py runserver $ai:$ap --insecure

