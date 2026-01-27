#!/usr/bin/env python

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List

import os
import math
import time

# Database imports.
from sqlalchemy import create_engine, Column, String, Float, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# Small function that waits if a file exists.
# We do this to be sure we don't access a database while it's
# being updated.
def waitOnFile(file) :
    while os.path.exists(file) :
        time.sleep(0.25)
    return

# Small function that takes a lat/lon and a range (in Km) and
# a heading in degrees and returns the resulting lat/lon in a dictionary.
# Assumes earth's radius is constant.
def locationPlusRange(lat, lon, rangeKm, heading) :
    """
    Calculates the destination lat/lon given start point, 
    distance(km) and heading(degrees).
    """
    # Radius of the Earth in km
    R = 6371.0
    
    # Convert degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    heading_rad = math.radians(heading)
    
    # Calculate angular distance in radians
    angular_distance = rangeKm / R
    
    # Calculate destination latitude
    dest_lat_rad = math.asin(
        math.sin(lat_rad) * math.cos(angular_distance) +
        math.cos(lat_rad) * math.sin(angular_distance) * math.cos(heading_rad)
    )
    
    # Calculate destination longitude
    dest_lon_rad = lon_rad + math.atan2(
        math.sin(heading_rad) * math.sin(angular_distance) * math.cos(lat_rad),
        math.cos(angular_distance) - math.sin(lat_rad) * math.sin(dest_lat_rad)
    )
    
    # Convert back to degrees
    dest_lat = math.degrees(dest_lat_rad)
    dest_lon = math.degrees(dest_lon_rad)
    
    # Normalize longitude to -180 to +180
    dest_lon = (dest_lon + 540) % 360 - 180
    
    return {'lat': dest_lat, 'lon': dest_lon}



# Set up tags that appear in the documentation pages that FastAPI generates.
tags_metadata = [
    {
        "name":"bussinAPIs",
        "description":"Fast API endpoints in support of bussinFR",
        "externalDocs": {
            "description": "bussinFR repo",
            "url": "https://github.com/nilesOien/bussinFR",
        },
    },
    {
        "name":"bus-stop-service",
        "description":"Serves out locations and descriptions of bus stops in a specified area. The area can be specified directly with minimum and maximum lats and lons or a center lat and long with a range in Km can be specified. Directly specified minima/maxima are used preferably with center/range values being used only if directly specified minima/maxima are not specified.",
    }
   ]

# Get a FastAPI application object
bussinApp = FastAPI(title="bussinAPIs",
        summary="End points for bussinFR.",
        description="Used by javaScript to get the data.",
        contact={
          "name": "Niles Oien",
          "url": "https://github.com/nilesOien",
          "email": "nilesoien@gmail.com",
        },
        version="1.0.0",
        openapi_tags=tags_metadata)

# Bus stop end point.
class busStopServiceResponseClass(BaseModel) :
    """
    Pydantic class that defines the format of what the bus_stop_service serves out.
    """
    stopid:   str
    stopname: str
    stopdesc: str
    lat:      float
    lon:      float

# Serve out bus stop location, description.
@bussinApp.get("/busStopService", tags=['bus-stop-service'], response_model=List[busStopServiceResponseClass])
async def get_bus_stops(minLat:     float = Query(default=None),
                        minLon:     float = Query(default=None),
                        maxLat:     float = Query(default=None),
                        maxLon:     float = Query(default=None),
                        centerLat:  float = Query(default=None),
                        centerLon:  float = Query(default=None),
                        rangeKm:    float = Query(default=None)):
    """
    Returns bus stop information for a specified area.
    """

    # The variables we're actually going to use.
    min_lat=None
    min_lon=None
    max_lat=None
    max_lon=None

    # If the filter variables are set directly, use them.
    numFilt=0
    if minLat is not None :
        min_lat=minLat
        numFilt += 1

    if minLon is not None :
        min_lon=minLon
        numFilt += 1

    if maxLat is not None :
        max_lat=maxLat
        numFilt += 1

    if minLon is not None :
        max_lon=maxLon
        numFilt += 1

    # If we don't have all 4 filters set directly...
    if numFilt < 4 :
        # And we do have a center lat/lon with range...
        if centerLat is not None and centerLon is not None and rangeKm is not None :
            # Then try to set the filters from center and range.
            if min_lat is None :
                d=locationPlusRange(centerLat, centerLon, rangeKm, 180.0) # Go south (180.0) to get min lat
                min_lat=d['lat']
            if min_lon is None :
                d=locationPlusRange(centerLat, centerLon, rangeKm, 270.0) # Go west (270.0) to get min lon
                min_lon=d['lon']
            if max_lat is None :
                d=locationPlusRange(centerLat, centerLon, rangeKm, 0.0) # Go north (0.0) to get max lat
                max_lat=d['lat']
            if max_lon is None :
                d=locationPlusRange(centerLat, centerLon, rangeKm, 90.0) # Go east (90.0) to get max lon
                max_lon=d['lon']


    # Database table ORM model.
    Base = declarative_base()
    class stopsTable(Base):
        __tablename__='stops'
        stopid   = Column(String, nullable=False, primary_key=True)
        stopname = Column(String, nullable=False)
        stopdesc = Column(String, nullable=False)
        lat      = Column(Float,  nullable=False)
        lon      = Column(Float,  nullable=False)
        __table_args__ = (UniqueConstraint('stopid', name='unique_constraint'),)

    # Database URL and block file. Depends on if we're in testing mode, which
    # is set through the BFR_TEST_MODE env var (which has to be set to either ON or TRUE
    # (case insensitive) to activate test mode).
    db_dir='databases'
    testMode=False
    test_env = os.getenv('BFR_TEST_MODE', 'OFF')
    if test_env.lower() == 'on' or test_env.lower() == 'true' :
        testMode=True

    if testMode :
        db_dir='test_databases'

    db_url="sqlite:///../" + db_dir + "/stops/database.db"
    db_block_file="../" + db_dir + "/stops/db_offline.marker"

    # Connect to the database.
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Set up basic query.
    query = db.query(stopsTable)

    # Add filters.
    if min_lat is not None :
        query = query.filter(stopsTable.lat >= min_lat)

    if min_lon is not None :
        query = query.filter(stopsTable.lon >= min_lon)

    if max_lat is not None :
        query = query.filter(stopsTable.lat <= max_lat)

    if max_lon is not None :
        query = query.filter(stopsTable.lon <= max_lon)

    query = query.order_by(stopsTable.lat)

    waitOnFile(db_block_file)

    db_results = query.all()

    db.close()

    return db_results

