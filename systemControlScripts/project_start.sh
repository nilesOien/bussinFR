#!/bin/bash

if [ ! -f ../cron_main.tab ]
then
 echo Cannot find crontab file - run project setup script
 exit -1
fi

crontab ../cron_main.tab

cd ../databases/trip_updates
./cron_monitor.sh ../../environment.vars

cd ../vehicles
./cron_monitor.sh ../../environment.vars

cd ../../webservices
./cron_monitor.sh ../environment.vars

exit 0

