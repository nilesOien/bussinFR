#!/bin/bash

# Script to configure and set up the project.
# Has to be run from this directory.

# Set program name
pn=`basename $0`

# Get the configuration name
if [ "$#" -ne 1 ]
then
 echo $pn : A configuration is required on the command line, for example :
 echo $pn rtd
 exit -1
fi

conf="$1"
if [ ! -d ../configs/"$conf" ]
then
 echo $pn : Configuration directory ../configs/"$conf" not found
 exit -1
fi

# Copy the config files into place if they do not already exist
for fn in config.json  cron_main.tab  environment.vars
do
 if [ ! -f ../configs/"$conf"/"$fn" ]
 then
  echo $pn : Required config file ../configs/"$conf"/"$fn" not found
  exit -1
 fi
done

if [ ! -f ../cron_main.tab ]
then
 cp -v ../configs/"$conf"/cron_main.tab ../cron_main.tab
else
 echo $pn : Already have ../cron_main.tab
fi

if [ ! -f ../environment.vars ]
then
 cp -v ../configs/"$conf"/environment.vars ../environment.vars
else
 echo $pn Already have ../environment.vars
fi

if [ ! -f ../webpages/config.json ]
then
 cp -v ./configs/"$conf"/config.json ../webpages/config.json
else
 echo $pn : Already have ../webpages/config.json
fi

# Check that we have uv installed.
which uv &> /dev/null
status="$?"
if [ "$status" -ne 0 ]
then
 echo uv command not found, please install it
 exit 0
fi

# Set up python env with the modules we need.
cd ..
if [ ! -f pyproject.toml ]
then
 uv init --name bussinFR --description "GTFS near real time display system" --bare .
 uv add -r requirements.in
else
 echo Project already set up with uv
fi

# Set up the test databases for unit tests
cd test_databases/trip_updates
if [ ! -f database.db ]
then
 ./make_db.sh
else
 echo Test DB for trip_updates already exists
fi

cd ../vehicles
if [ ! -f database.db ]
then
 ./make_db.sh
else
 echo Test DB for vehicles already exists
fi

cd ../stops
if [ ! -f database.db ]
then
 ./make_db.sh
else
 echo Test DB for stops already exists
fi

# Run the unit tests for coverage
cd ../../tests
if [ ! -d bussinFR_coverage ]
then
 ./run_tests_coverage.sh
else
 echo Unit tests for coverage have already been run
fi

exit 0

