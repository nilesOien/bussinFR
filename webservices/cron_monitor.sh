#!/bin/bash

# Script to be called from cron to keep uvicorn server
# running. Run in cron something like this :
# * * * * * $HOME/bussinFR/webservices/cron_monitor.sh $HOME/bussinFR/environment.vars > /dev/null 2>&1;
# To check every minute that uvicorn is running.

# Check that crontab is installed, exit if not.
cronCount=`crontab -l 2> /dev/null | wc -l`
if [ "$cronCount" -eq 0 ]
then
 echo No crontab, exiting
 exit 0
fi

# Needed to run under cron : If the file
# $HOME/.local/bin/env exists then
# source it so that uv will be found.
if [ -f "$HOME/.local/bin/env" ]
then
 source "$HOME/.local/bin/env"
fi

pn=`basename $0`

# Get the username. Try $USER, $LOGNAME and the end of $HOME
# in that order.
if [ -z "$USER" ]
then
 if [ -z "$LOGNAME" ]
 then
  # Try to get it from the home dir name
  un=`basename "$HOME"`
 else
  # Use LOGNAME
  un="$LOGNAME"
 fi
else
 un="$USER"
fi

# Get the environment file from the command line and source it.
if [ "$#" -ne 1 ]
then
 echo $pn : An environment file is required on the command line
 exit -1
fi

envFile="$1"
if [ ! -f "$envFile" ]
then
 echo $pn : Environment file $envFile not found
 exit -1
fi

source "$envFile"

cd "$BFR_TOP_DIR"/webservices

numRunning=`ps aux | grep "$un" | grep uvicorn | grep -v grep | wc -l`
echo $numRunning uvicorn processes running

if [ "$numRunning" -ne 0 ]
then
 exit 0
fi

echo Starting uvicorn
./start_server.sh ../environment.vars &> /dev/null &

exit 0

