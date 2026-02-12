#!/bin/bash

# Script to be called from cron to keep uvicorn server
# running. Run in cron something like this :
# * * * * * $HOME/bussinFR/webservices/cron_monitor.sh $HOME/bussinFR/environment.vars &> /dev/null
# To check every minute that uvicorn is running.

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

cd "$BFR_TOP_DIR"/webservices

numRunning=`ps aux | grep $USER | grep uvicorn | grep -v grep | wc -l`
echo $numRunning uvicorn processes running

if [ "$numRunning" -ne 0 ]
then
 exit 0
fi

echo Starting uvicorn
./start_server.sh &> /dev/null &

exit 0

