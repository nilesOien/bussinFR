#!/usr/bin/env python

# Do the imports.
from google.transit import gtfs_realtime_pb2
import requests
import argparse
import sys
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine, UniqueConstraint, Column, String, Float, Integer
from pathlib import Path
from sqlalchemy import insert, select
from sqlalchemy.dialects.mysql import BIGINT
import time
import os

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




# Get the URL from the url argument.
parser = argparse.ArgumentParser(description='Dump realtime transport data from RTD.')
parser.add_argument('--url', required=True, type=str, help='The RTD URL to dump.')
args = parser.parse_args()

# Initialize a FeedMessage object
feed = gtfs_realtime_pb2.FeedMessage()

# Get the URL from the --url option on the command line.
url = args.url

# Fetch and parse the data
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status() # Raise an exception for bad status codes
    feed.ParseFromString(response.content)

except requests.exceptions.RequestException as e:
    print(f"Error fetching data: {e}")
    sys.exit(-1)

# Iterate over the entities and print information
print(f"There are {len(feed.entity)} entities in the feed {args.url}")

# Database table looks like :
# CREATE TABLE vehicles_update (
#	route VARCHAR NOT NULL, 
#	schedule_relationship INTEGER NOT NULL, 
#	direction_id INTEGER NOT NULL, 
#	current_status INTEGER NOT NULL, 
#	timestamp BIGINT NOT NULL, 
#	lat FLOAT NOT NULL, 
#	lon FLOAT NOT NULL, 
#	bearing FLOAT NOT NULL, 
#	PRIMARY KEY (route)
# )
# So the dictionaries in our list should have those keys.

vehicleList = []
for entity in feed.entity:
    # Print different types of data based on what the entity contains

    if entity.HasField('vehicle'):
        d={}
        d['route']          = entity.vehicle.trip.route_id
        d['schedule_relationship']    = entity.vehicle.trip.schedule_relationship
        d['direction_id']   = entity.vehicle.trip.direction_id
        d['current_status'] = entity.vehicle.current_status
        d['timestamp']      = entity.vehicle.timestamp
        d['lat']            = entity.vehicle.position.latitude
        d['lon']            = entity.vehicle.position.longitude
        d['bearing']        = entity.vehicle.position.bearing
        vehicleList.append(d)

Base = declarative_base()

class vehiclesTable(Base):
    __tablename__='vehicles'
    id             = Column(Integer, nullable=False, primary_key=True)
    route          = Column(String,  nullable=False)
    schedule_relationship = Column(Integer, nullable=False)
    direction_id   = Column(Integer, nullable=False)
    current_status = Column(Integer, nullable=False)
    timestamp      = Column(BIGINT(unsigned=True), nullable=False)
    lat            = Column(Float,   nullable=False)
    lon            = Column(Float,   nullable=False)
    bearing        = Column(Float,   nullable=False)

class vehiclesUpdateTable(Base):
    __tablename__='vehicles_update'
    id             = Column(Integer, nullable=False, primary_key=True)
    route          = Column(String,  nullable=False)
    schedule_relationship = Column(Integer, nullable=False)
    direction_id   = Column(Integer, nullable=False)
    current_status = Column(Integer, nullable=False)
    timestamp      = Column(BIGINT(unsigned=True), nullable=False)
    lat            = Column(Float,   nullable=False)
    lon            = Column(Float,   nullable=False)
    bearing        = Column(Float,   nullable=False)

engine = create_engine("sqlite:///database.db", echo=False)


# Delete all entries in the update table.
Session = sessionmaker(bind=engine)
session = Session()
session.query(vehiclesUpdateTable).delete(synchronize_session=False)
session.commit()

# Insert what we have in our list that we just got into the update table.
ok=False
try:
    # Use bulk_insert_mappings (more efficient for large datasets)
    session.bulk_insert_mappings(vehiclesUpdateTable, vehicleList)
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

# ...and then pull the database offline, delete what we have in
# our "real" table, and then copy the update table into the "real" table,
# and finally put the DB back online.

# Put the database offline
put_db_offline()

# Delete everything in the current "real" table.
session.query(vehiclesTable).delete(synchronize_session=False)
session.commit()

# Copy from the update table to the "real" table.
# Make a select statement on update table...
select_stmt = select(vehiclesUpdateTable)
# ...and use that select statement in an insert statement on the "real" table.
insert_stmt = insert(vehiclesTable).from_select(
    vehiclesTable.__table__.columns.keys(), select_stmt
)
session.execute(insert_stmt)
session.commit()

# Put the database back online.
put_db_online()

print("Success!")

sys.exit(0)



