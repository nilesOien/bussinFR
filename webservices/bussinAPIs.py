#!/usr/bin/env python

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List

import os
import time

# Database imports.
from sqlalchemy import create_engine, Column, String, Float, Integer, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import BIGINT

# Small function that waits if a file exists.
# We do this to be sure we don't access a database while it's
# being updated.
def waitOnFile(file) :
    while os.path.exists(file) :
        time.sleep(0.25)
    return

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
        "description":"Serves out locations and descriptions of bus stops in a specified area.",
    },
    {
        "name":"vehicle-service",
        "description":"Serves out locations and descriptions of vehicles in a specified area. For the current_status field, 2=Moving 1=Stopped",
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
                        maxLon:     float = Query(default=None)):
    """
    Returns bus stop information for a specified area.
    """

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
    if minLat is not None :
        query = query.filter(stopsTable.lat >= minLat)

    if minLon is not None :
        query = query.filter(stopsTable.lon >= minLon)

    if maxLat is not None :
        query = query.filter(stopsTable.lat <= maxLat)

    if maxLon is not None :
        query = query.filter(stopsTable.lon <= maxLon)

    query = query.order_by(stopsTable.lat)

    waitOnFile(db_block_file)

    db_results = query.all()

    db.close()

    return db_results





# Vehicle end point.
class vehicleServiceResponseClass(BaseModel) :
    """
    Pydantic class that defines the format of what the vehicle end point serves out.
    """
    route:   str
    timestamp: int
    current_status: int
    lat:      float
    lon:      float
    bearing:  float

# Serve out vehicle information.
@bussinApp.get("/vehicleService", tags=['vehicle-service'], response_model=List[vehicleServiceResponseClass])
async def get_vehicles(minLat:     float = Query(default=None),
                       minLon:     float = Query(default=None),
                       maxLat:     float = Query(default=None),
                       maxLon:     float = Query(default=None)):
    """
    Returns vehicle information for a specified area.
    """

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

    db_url="sqlite:///../" + db_dir + "/vehicles/database.db"
    db_block_file="../" + db_dir + "/vehicles/db_offline.marker"

    # Connect to the database.
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Set up query but not all columns - only selected ones.
    query = db.query(vehiclesTable).with_entities(vehiclesTable.route, vehiclesTable.timestamp,
                                vehiclesTable.current_status, vehiclesTable.lat, vehiclesTable.lon, vehiclesTable.bearing)

    # Add filters.
    if minLat is not None :
        query = query.filter(vehiclesTable.lat >= minLat)

    if minLon is not None :
        query = query.filter(vehiclesTable.lon >= minLon)

    if maxLat is not None :
        query = query.filter(vehiclesTable.lat <= maxLat)

    if maxLon is not None :
        query = query.filter(vehiclesTable.lon <= maxLon)

    query = query.order_by(vehiclesTable.lat)

    waitOnFile(db_block_file)

    db_results = query.all()

    db.close()

    return db_results


