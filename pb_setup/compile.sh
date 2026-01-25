#!/bin/bash

# Get and compile the gtfs protoc file using protoc.
# This creates a python file that is imported in python
# to deal with the realtime data that is in the protbuf format.
#
# Niles Oien January 2026

# Get the gtfs proto file, if we do not have it.
if [ ! -f gtfs-realtime.proto ]
then
 curl -L -O https://gtfs.org/documentation/realtime/gtfs-realtime.proto
fi

if [ ! -f gtfs-realtime.proto ]
then
 echo Failed to fetch gtfs-realtime.proto
 exit -1
fi

# Compile the proto file, if we have not done that.
if [ ! -f gtfs_realtime_pb2.py ]
then
 protoc --python_out=. gtfs-realtime.proto --proto_path=.
fi

if [ ! -f gtfs_realtime_pb2.py ]
then
 echo failed to compile gtfs-realtime.proto into gtfs_realtime_pb2.py
 exit -1
fi

echo Success!

exit 0

