#!/bin/bash

# Update the bus stop database.
# May want to run this in cron like so :
# 0 23 * * sat $HOME/bussinFR/databases/stops/dbUpdate.sh $HOME/bussinFR/environment.vars > $HOME/bussinFR/databases/stops/dbUpdate.log 2>&1;
# for weekly updates.
#
# Needed to run under cron : If the file
# $HOME/.local/bin/env exists then
# source it so that uv will be found.
if [ -f "$HOME/.local/bin/env" ]
then
 source "$HOME/.local/bin/env"
fi

# Set program name and note start time.
pn=`basename $0`
startTm=`date --utc +%s`

# Get the environment file from the command line and source it.
if [ "$#" -ne 1 ]
then
 echo $pn : An environment file is required on the command line, eg $pn $HOME/bussinFR/environment.vars
 exit -1
fi

envFile="$1"
if [ ! -f "$envFile" ]
then
 echo $pn : Environment file $envFile not found
 exit -1
fi

source "$envFile"
env | grep BFR_

if [ ! -d "$BFR_TOP_DIR"/databases/stops ]
then
 echo $pn : Directory $BFR_TOP_DIR/databases/stops not found
 exit -1
fi

cd "$BFR_TOP_DIR"/databases/stops

zip_base=`basename "$BFR_STOPS_ZIP_URL"`

echo $pn : Fetching $zip_base from $BFR_STOPS_ZIP_URL

rm -rf fromAgency
mkdir fromAgency
cd fromAgency/

curl -O -L "$BFR_STOPS_ZIP_URL"
if [ ! -f "$zip_base" ]
then
 echo $pn : Failed to fetch $zip_base from $BFR_STOPS_ZIP_URL
 exit -1
fi

unzip -q "$zip_base"
if [ "$?" -ne 0 ]
then
 echo $pn : Failed to unzip $zip_base
 exit -1
fi

if [ ! -f "$BFR_STOPS_FILE" ]
then
 echo $pn : $BFR_STOPS_FILE not found in zip archive from $BFR_STOPS_ZIP_URL
 exit -1
fi

cd ..

numLines=`cat fromAgency/"$BFR_STOPS_FILE" | wc -l`
echo $numLines lines in $BFR_STOPS_FILE from $BFR_STOPS_ZIP_URL - processing

# If the database does not exist, initialize it.
if [ ! -f database.db ]
then
 echo $pn : Initializing database
 uv run ./init_db.py
fi

if [ ! -f database.db ]
then
 echo $pn : Failed to initialize database
 exit -1
fi

# Do the database update.
uv run ./update_db.py --stopFile fromAgency/"$BFR_STOPS_FILE"
if [ "$?" -ne 0 ]
then
 echo Database update failed
 exit -1
fi

# Write a file so we know when we last updated and how long it took.
endTm=`date --utc +%s`
endDt=`date --date=@"$endTm" +"%Y/%m/%d %H:%M:%S %Z"`
durationSec=`expr "$endTm" - "$startTm"`

echo {\"updated\":\""$endDt"\", \"utim\":"$endTm", \"durationSec\":"$durationSec" } > updated.time

exit 0

