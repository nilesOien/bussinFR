#!/usr/bin/env python

from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List

import os
import time
import datetime

# Database imports.
from sqlalchemy import create_engine, Column, String, Float, Integer, UniqueConstraint, or_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.mysql import BIGINT

### Add middleware for access.
###from fastapi.middleware.cors import CORSMiddleware

### Set up origins so anyone can get at the APIs.
###origins = ["*"]

# Now we do this instead :
from fastapi.staticfiles import StaticFiles
# so we can serve out the static files on the same port so
# there's no issue that needs middleware.

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
        "description":"Serves out locations and descriptions of bus stops in a specified area. For RTD, test with a minimum latitude of 40 (Baseline road)"
    },
    {
        "name":"vehicle-service",
        "description":"Serves out locations and descriptions of vehicles in a specified area. For the current_status field, 2=Moving 1=Stopped. Can also specify a comma separated list of routes (default is all routes). Internally spaces are removed from the list of routes and it is converted to upper case, so that \"bolt, jump\" becomes \"BOLT,JUMP\". To test for RTD, enter a minimum latitude of 40 (Baseline road)."
    },
    {
        "name":"trip-service",
        "description":"Serves out trip updates for a specified stop ID. Union Station in Denver has stop ID 34343 which may be a good test for that region."
    }
   ]

try:
    agency_name = os.environ["BFR_AGENCY_NAME"]
except KeyError:
    print("Error: BFR_AGENCY_NAME environment variable not set.")
    quit()
agency_name=agency_name.lower()

# Get a FastAPI application object
bussinApp = FastAPI(title="bussinAPIs",
        root_path="/" + agency_name,                  # Because we're deploying behind a gateway. Must match nginx settings.
        summary="End points for bussinFR.",
        description="Used by javaScript to get the data.",
        contact={
          "name": "Niles Oien",
          "url": "https://github.com/nilesOien",
          "email": "nilesoien@gmail.com",
        },
        version="1.0.0",
        openapi_tags=tags_metadata)

### Add middleware to allow all origins.
###bussinApp.add_middleware(
###        CORSMiddleware,
###        allow_origins=origins,
###        allow_methods=["*"],
###        allow_headers=["*"])


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
                       maxLon:     float = Query(default=None),
                       routesCSV:  str   = Query(default=None)):
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

    # Routes is a comma separated list of routes of interest.
    # Default is to serve all routes, but if this is specified,
    # the only serve these routes.

    if routesCSV is not None :
        routesCSV = routesCSV.upper()  # Convert entered route list to upper case
        routesCSV = "".join(routesCSV.split()) # Remove whitespaces
        routes=routesCSV.split(',')
        if len(routes) > 0 :
            # This next part is a bit tricky.
            # If the caller specified routesCSV="bolt, 205"
            # then routes is now the list [ "BOLT", "205" ].
            #
            # The * operator (the unpacking operator)
            # when used in a function call
            # takes an iterable (like a list or tuple) and
            # unpacks its elements as separate positional
            # arguments, so for example we can :
            # >>> x=[1,2,3]  # A list
            # >>> print(x)   #
            # [1, 2, 3]      # Printed the list
            # >>> print(*x)  #
            # 1 2 3          # Printed the list as positional parameters
            #
            # So we can pass the elements of a list
            # to the function as positional arguments
            # (in this case the or_()
            # function).
            #
            # So make the list of filters that we want to throw at or_() :
            route_filters = [vehiclesTable.route == route for route in routes]
            # And then use the unpacking operator to throw them all at or_()
            # as positional arguments :
            query = query.filter(or_(*route_filters))


    query = query.order_by(vehiclesTable.lat)

    waitOnFile(db_block_file)

    db_results = query.all()

    db.close()

    return db_results






# Trip update end point.
class tripServiceResponseClass(BaseModel) :
    """
    Pydantic class that defines the format of what the trip update end point serves out.
    """
    route:   str
    arrivaltime: int

# Serve out vehicle information.
@bussinApp.get("/tripService", tags=['trip-service'], response_model=List[tripServiceResponseClass])
async def get_trips(stopID:     str = Query(default=None)):
    """
    Returns trip update information for the specified stop ID.
    """

    if stopID is None :
        return []

    Base = declarative_base()

    class tripsTable(Base):
        __tablename__='intrepid_trips'
        id             = Column(Integer, nullable=False, primary_key=True)
        route          = Column(String,  nullable=False)
        schedule_relationship = Column(Integer, nullable=False)
        arrivaltime    = Column(BIGINT(unsigned=True), nullable=False)
        stopid         = Column(String,   nullable=False)


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

    db_url="sqlite:///../" + db_dir + "/trip_updates/database.db"
    db_block_file="../" + db_dir + "/trip_updates/db_offline.marker"

    # Connect to the database.
    engine = create_engine(db_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    # Set up query but not all columns - only selected ones.
    query = db.query(tripsTable).with_entities(tripsTable.route, tripsTable.arrivaltime)

    # Add filter on stop ID.
    query = query.filter(tripsTable.stopid == stopID)

    # Also add a filter so that we only serve out
    # arrival times that are in the future.
    current_utc_time = datetime.datetime.now(datetime.timezone.utc)
    current_unix_time = int(current_utc_time.timestamp())
    query = query.filter(tripsTable.arrivaltime >= current_unix_time)

    query = query.order_by(tripsTable.arrivaltime)

    waitOnFile(db_block_file)

    db_results = query.all()

    db.close()

    return db_results


# Mount for the static HTML/css/javaScript/favicon
# In the call below :
#
# * The first argument ("/") is the URL path where the files will be exposed,
#   so it will pop up as "http://localhost:8000/"
# * The second argument is the actual directory on this server,
#   and setting html=True will serve out index.html by default.
# * The third argument is an internal name that can be used for URL
#   generation in templates, often with the url_for function.
#
# Note that order matters. FastAPI matches requests *sequentially* so
# we define this last so that it will try the API end points first.
# Follow sym links to show test coverage results.
bussinApp.mount("/", StaticFiles(directory="../webpages", html=True, follow_symlink=True), name="webpages")


