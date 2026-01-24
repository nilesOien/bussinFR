#!/usr/bin/env python

# Read the file that lists stops (from the agency) and write
# it to the database. The file looks something like this :
#
# stop_id,stop_code,stop_name,stop_desc,stop_lat,stop_lon,zone_id,stop_url,location_type,parent_station,stop_timezone,wheelchair_boarding,platform_code
# 34385,34385,Wewatta St & 17th St,Vehicles Travelling Northeast,39.754143,-105.001356,34385,,0,,,1,
# 26188,26188,Arapahoe at Village Center Station Gate D,Vehicles Travelling East,39.601134,-104.887857,26188,,0,,,1,D  {1409}
# 35451,35451,A Basin,Vehicles Travelling East,39.642721,-105.871835,35451,,0,,,1,
# 35176,35176,West Glenwood Park & Ride,Vehicles Travelling North,39.557502,-107.353704,35176,,0,,,1,
# 35471,35471,Wooly Mammoth Park & Ride,Vehicles Travelling South,39.697713,-105.207457,35471,,0,,,1,
#
# Database tables look like this :
# CREATE TABLE stops (
#	stopid VARCHAR NOT NULL, 
#	stopname VARCHAR NOT NULL, 
#	stopdesc VARCHAR NOT NULL, 
#	lat FLOAT NOT NULL, 
#	lon FLOAT NOT NULL, 
#	PRIMARY KEY (stopid), 
#	CONSTRAINT unique_constraint UNIQUE (stopid)
# );
# CREATE TABLE stops_update (
#	stopid VARCHAR NOT NULL, 
#	stopname VARCHAR NOT NULL, 
#	stopdesc VARCHAR NOT NULL, 
#	lat FLOAT NOT NULL, 
#	lon FLOAT NOT NULL, 
#	PRIMARY KEY (stopid), 
#	CONSTRAINT unique_constraint UNIQUE (stopid)
# );
#
# First we read the file. Then
# we delete everything in the database table stops_update,
# then we write the file information into
# stops_update, then make a marker file that marks the database
# as being offline, then delete everything in the stops table,
# then copy from stops_update into stops (faster so that the
# database is only offline for a moment).

import argparse
import os
import sys
import pprint
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, UniqueConstraint, Column, String, Float
from pathlib import Path
from sqlalchemy import insert, select
import time


# The name of the marker file that indicates that the database is offline.
marker_file="db_offline.marker"

# Small function to write the marker file that marks the DB as being offline
# to the rest of this system.
# The file does not need content, it simply must exist.
def put_db_offline() :
    print("Taking database offline and waiting for clients to finish...")
    Path(marker_file).touch()
    # Sleep to allow clients to finish
    time.sleep(2)
    return

# Small function to put the database back online to the rest of this system.
# It just removes the marker file.
def put_db_online() :
    print("Putting database back online")
    if os.path.exists(marker_file):
        os.remove(marker_file)
    else :
        print("Went to put database back online... and found that it already was?")
    return

# Parse command line args.
parser = argparse.ArgumentParser(description='Update the database of bus stops.')
parser.add_argument('--stopFile', required=True, type=str, help='The file of bus stops from the agency.')
parser.add_argument('--verbose', action='store_true', help='Activate verbose messaging.')
args = parser.parse_args()

# Read the input file.
if not os.path.isfile(args.stopFile) :
    print(f"Stops file {args.stopFile} not found")
    sys.exit(-1)

lines_list = []
with open(args.stopFile, 'r') as file:
    lines_list = file.readlines()

print(f"Read {len(lines_list)} lines from {args.stopFile} including header")

first_line = True
stop_list = []
line_num=0
for line in lines_list :
    line_num += 1
    # Skip the first line, it's a header.
    if first_line :
        first_line = False
        continue

    items = line.split(',')

    if len(items) < 6 :
        print(f"Skipping line {line_num} of {args.stopFile} as there are too few items : {line}")
        continue

    try:
        lat = float(items[4])
    except ValueError:
        print(f"Skipping line {line_num} of {args.stopFile} as could not convert '{items[4]}' to a float for latitude.")
        continue

    try:
        lon = float(items[5])
    except ValueError:
        print(f"Skipping line {line_num} of {args.stopFile} as could not convert '{items[5]}' to a float for longitude.")
        continue

    d = { "stopid":items[0], "stopname":items[2], "stopdesc":items[3], "lat":lat, "lon":lon }
    stop_list.append(d)
    
if args.verbose :
    pprint.pprint(stop_list)

# OK, the file information is now in stop_list, a list of dictionaries
# with keys having the same name as the database columns.

# Define ORM table classes.
Base = declarative_base()

class stopsTable(Base):
    __tablename__='stops'
    stopid   = Column(String, nullable=False, primary_key=True)
    stopname = Column(String, nullable=False)
    stopdesc = Column(String, nullable=False)
    lat      = Column(Float,  nullable=False)
    lon      = Column(Float,  nullable=False)
    __table_args__ = (UniqueConstraint('stopid', name='unique_constraint'),)

class stopsTableUpdate(Base):
    __tablename__='stops_update'
    stopid   = Column(String, nullable=False, primary_key=True)
    stopname = Column(String, nullable=False)
    stopdesc = Column(String, nullable=False)
    lat      = Column(Float,  nullable=False)
    lon      = Column(Float,  nullable=False)
    __table_args__ = (UniqueConstraint('stopid', name='unique_constraint'),)

# Get the engine.
engine = create_engine("sqlite:///database.db", echo=False)

# Delete all entries in the stops_update table.
Session = sessionmaker(bind=engine)
session = Session()
session.query(stopsTableUpdate).delete(synchronize_session=False)
session.commit()

# Insert what we have in stop_list into stopsTableUpdate
ok=False
try:
    # Use bulk_insert_mappings (more efficient for large datasets)
    session.bulk_insert_mappings(stopsTableUpdate, stop_list)
    session.commit()
    print("Data inserted into update successfully.")
    ok=True

except Exception as e:
    session.rollback() # Rollback on error
    print(f"Error inserting data into update : {e}")
    ok=False

finally:
    session.close()

if not ok :
    print("Failed to insert into stops update table.")
    sys.exit(-1)

# OK, if we got to here then the new data are in stopsTableUpdate and
# the old data are in stopsTable. We write a marker file to pull the
# database offline, then delete the old data in stopsTable, then
# copy the new data from stopsTableUpdate into stopsTable.

# Take the database offline while we do this.
put_db_offline()

# Delete everything in the current stops table.
session.query(stopsTable).delete(synchronize_session=False)
session.commit()

# Copy from stopsTableUpdate to stopsTable.
# Make a select statement on stopsUpdateTable...
select_stmt = select(stopsTableUpdate)
# ...and use that select statement in an insert statement on stopsTable
insert_stmt = insert(stopsTable).from_select(
    stopsTable.__table__.columns.keys(), select_stmt
)
session.execute(insert_stmt)
session.commit()

# Put the database back online.
put_db_online()

print("Success!")

sys.exit(0)

