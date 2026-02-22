#!/bin/bash


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
env | grep BFR_UVICORN

if [ ! -d "$BFR_TOP_DIR"/webservices ]
then
 echo $pn : Directory $BFR_TOP_DIR/webservices not found
 exit -1
fi

cd "$BFR_TOP_DIR"/webservices

uv run uvicorn bussinAPIs:bussinApp --host "$BFR_UVICORN_HOST" --port "$BFR_UVICORN_PORT" --workers "$BFR_UVICORN_WORKERS"

exit 0

