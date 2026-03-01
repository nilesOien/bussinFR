#!/bin/bash

#crontab -r

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

echo Assuming username $un

# Kill uvicorn
ps aux | grep "$un" | grep uvicorn | grep -v grep | awk '{print $2}' | while IFS= read -r pid
do
 echo Killing uvicorn PID $pid
 kill -9 "$pid"
done
echo

# Kill fetchVehicleUpdates.sh
ps aux | grep "$un" | grep fetchVehicleUpdates.sh | grep -v grep | awk '{print $2}' | while IFS= read -r pid
do
 echo Killing fetchVehicleUpdates.sh PID $pid
 kill -9 "$pid"
done
echo

# Kill fetchTripUpdates.sh
ps aux | grep "$un" | grep fetchTripUpdates.sh | grep -v grep | awk '{print $2}' | while IFS= read -r pid
do
 echo Killing fetchTripUpdates.sh PID $pid
 kill -9 "$pid"
done
echo

exit 0

