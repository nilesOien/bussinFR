#!/bin/bash

# Script to be called from cron to keep trip fetches to the database
# running. Run in cron something like this :
# * * * * * $HOME/bussinFR/databases/trip_updates/cron_monitor.sh $HOME/bussinFR/environment.vars > /dev/null 2>&1;
# To check every minute that the fetch is running.

# Needed to run under cron : If the file
# $HOME/.local/bin/env exists then
# source it so that uv will be found.
if [ -f "$HOME/.local/bin/env" ]
then
 source "$HOME/.local/bin/env"
fi

pn=`basename $0`

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

cd "$BFR_TOP_DIR"/databases/trip_updates

proc="./fetchTripUpdates.sh $envFile $BFR_AGENCY_NAME"

echo $pn : Looking for process :
echo $proc

numRunning=`ps aux | grep $USER | grep "$proc" | grep -v grep | wc -l`
echo $numRunning such processes running

if [ "$numRunning" -ne 0 ]
then
 exit 0
fi

echo Starting
./fetchTripUpdates.sh $envFile $BFR_AGENCY_NAME &> /dev/null &

exit 0

