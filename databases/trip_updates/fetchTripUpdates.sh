#!/bin/bash

pn=`basename $0`
startTm=`date --utc +%s`

# Get the environment file from the command line and source it.
if [ "$#" -ne 2 ]
then
 echo $pn : An environment file is required on the command line as well as an agency, eg
 echo $pn $HOME/bussinFR/environment.vars CODOT
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

while [ 1 -eq 1 ]
do

 # Re-source the env file for realtime updates
 source "$envFile"

 # Stop if the stop maker is present
 if [ -f "stop.marker" ]
 then
  echo Stopping...
  exit 0
 fi

 # Hold if the hold marker is present
 while [ -f "hold.marker" ]
 do
  echo Holding...
  sleep 1
 done

 # Create the database if it does not exist
 if [ ! -f "database.db" ]
 then
  uv run ./init_db.py
  status="$?"
  if [ "$status" -ne 0 ]
  then
   echo Failed to init db
   exit -1
  fi
 fi

 startTm=`date --utc +%s`

 uv run update_db.py --url "$BFR_TRIPS_URL"
 status="$?"
 if [ "$status" -ne 0 ]
 then
  echo Failed to update db
  exit -1
 fi

 # Write a file so we know when we last updated and how long it took.
 endTm=`date --utc +%s`
 endDt=`date --date=@"$endTm" +"%Y/%m/%d %H:%M:%S %Z"`
 durationSec=`expr "$endTm" - "$startTm"`

 echo {\"updated\":\""$endDt"\", \"utim\":"$endTm", \"durationSec\":"$durationSec" } > updated.time
 cat updated.time

 # Calculate roughly how long we should sleep for in order to
 # meet the polling spec. 
 sleepSec=`expr "$BFR_TRIP_POLL" - "$durationSec"`
 if [ "$sleepSec" -gt 0 ]
 then
  echo Sleeping for $sleepSec seconds
  sleep "$sleepSec"
 fi

 echo

done # End of eternal loop

exit 0

