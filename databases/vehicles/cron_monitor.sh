#!/bin/bash

# Script to be called from cron to keep vehicle fetches to the database
# running. Run in cron something like this :
# * * * * * $HOME/bussinFR/databases/vehicles/cron_monitor.sh $HOME/bussinFR/environment.vars &> /dev/null
# To check every minute that the fetch is running.

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

cd "$BFR_TOP_DIR"/databases/vehicles

proc="./fetchVehicleUpdates.sh $envFile $BFR_AGENCY_NAME"

echo $pn : Looking for process :
echo $proc

numRunning=`ps aux | grep "$proc" | grep -v grep | wc -l`
echo $numRunning such processes running

if [ "$numRunning" -ne 0 ]
then
 exit 0
fi

echo Starting
./fetchVehicleUpdates.sh $envFile $BFR_AGENCY_NAME &> /dev/null &

exit 0

