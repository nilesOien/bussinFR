#!/usr/bin/env python

# Initialize the database.

from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.mysql import BIGINT
import sys

# Make the table.
Base = declarative_base()

class tripsTable(Base):
    __tablename__='intrepid_trips'
    id             = Column(Integer, nullable=False, primary_key=True)
    route          = Column(String,  nullable=False)
    schedule_relationship = Column(Integer, nullable=False)
    arrivaltime    = Column(BIGINT(unsigned=True), nullable=False)
    stopid         = Column(String,   nullable=False)

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

tlist=[]
for i in range(11) :
    d={}
    d['route']=f"BUS{i:0{2}d}"
    d['schedule_relationship']=0
    d['arrivaltime']=0
    d['stopid']='STP01'

    tlist.append(d)

for i in range(5) :
    d={}
    d['route']=f"BUS{i:0{2}d}"
    d['schedule_relationship']=0
    d['arrivaltime']=0
    d['stopid']='STP02'

    tlist.append(d)



Session = sessionmaker(bind=engine)
session = Session()

ok=False
try:
    # Use bulk_insert_mappings (more efficient for large datasets)
    session.bulk_insert_mappings(tripsTable, tlist)
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

