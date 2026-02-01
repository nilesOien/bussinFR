#!/usr/bin/env python

# Initialize the database.

from sqlalchemy import create_engine, Column, String, Float, Integer
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.mysql import BIGINT
import sys

# Make the table.
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

# Create the database.
# Had to install sqlalchemy_utils to do this.
engine = create_engine("sqlite:///database.db", echo=False)

Base.metadata.create_all(engine)

if not database_exists(engine.url):
    create_database(engine.url)

# Drop any existing version of that table.
Base.metadata.drop_all(engine)

# OK, now create the empty tables. Turn echo on, just for this.
engine.echo=True
Base.metadata.create_all(engine)
engine.echo=False

vlist=[]
for i in range(20) :
    d={}
    d['route']=f"BUS{i:0{2}d}"
    d['schedule_relationship']=0
    d['direction_id']=0
    d['current_status']=2
    d['timestamp']=0
    d['lat']=i-10
    d['lon']=10-i
    d['bearing']=i*0.5

    vlist.append(d)

Session = sessionmaker(bind=engine)
session = Session()

ok=False
try:
    # Use bulk_insert_mappings (more efficient for large datasets)
    session.bulk_insert_mappings(vehiclesTable, vlist)
    session.commit()
    print("Data inserted successfully.")
    ok=True

except Exception as e:
    session.rollback() # Rollback on error
    print(f"Error inserting data : {e}")
    ok=False

finally:
    session.close()

# That's all - the database should be created.
if ok :
    print("Normal termination.")
else :
    print("Something went wrong")

sys.exit(0)

