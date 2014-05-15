#!/bin/bash

NAME="octal_content"
OCTALDIR=/srv/octal/octal-application
FLASKDIR=$OCTALDIR/content_server

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $FLASKDIR
source ../../meta_venv/bin/activate
export PYTHONPATH=$OCTALDIR:$PYTHONPATH

exec uwsgi -s /srv/content.sock -w server:app --chmod-socket=666
