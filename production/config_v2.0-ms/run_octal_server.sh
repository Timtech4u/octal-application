#!/bin/bash
 
NAME="octal"                                      # Name of the application
DJANGODIR=/srv/octal/octal-application/server     # Django project directory
SOCKFILE=/srv/octal.sock                          # we will communicte using this unix socket
USER=octal                                        # the user to run as
GROUP=octal                                       # the group to run as
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=server.settings            # which settings file should Django use
DJANGO_WSGI_MODULE=server.wsgi                    # WSGI module name
 
echo "Starting $NAME as `whoami`"
 
# Activate the virtual environment
cd $DJANGODIR
source ../../meta_venv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
#export PYTHONPATH=$DJANGODIR:$PYTHONPATH
 
# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR
 
# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user=$USER --group=$GROUP \
  --log-level=debug \
  --bind=unix:$SOCKFILE
#  --bind=0.0.0.0:8080

