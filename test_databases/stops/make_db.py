#!/usr/bin/env python

# Write a bus stop database to test against.
# Initialize the database.

from sqlalchemy import create_engine, UniqueConstraint, Column, String, Float
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base, sessionmaker

# Make the table.
Base = declarative_base()

class stopsTable(Base):
    __tablename__='stops'
    stopid   = Column(String, nullable=False, primary_key=True)
    stopname = Column(String, nullable=False)
    stopdesc = Column(String, nullable=False)
    lat      = Column(Float,  nullable=False)
    lon      = Column(Float,  nullable=False)
    __table_args__ = (UniqueConstraint('stopid', name='unique_constraint'),)

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

stplist=[]
for i in range(20) :
    stpid = f"{i:0{4}d}"
    print(stpid)
    stpname=f"Bus stop {stpid}"
    stpdesc=f"Description of stop {stpid}"
    stplat=i-10
    stplon=-stplat
    d={"stopid":stpid, "stopname":stpname, "stopdesc":stpdesc, "lat":stplat, "lon":stplon }

    stplist.append(d)

Session = sessionmaker(bind=engine)
session = Session()

ok=False
try:
    # Use bulk_insert_mappings (more efficient for large datasets)
    session.bulk_insert_mappings(stopsTable, stplist)
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

quit()

