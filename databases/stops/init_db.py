#!/usr/bin/env python

# Initialize the database.

from sqlalchemy import create_engine, UniqueConstraint, Column, String, Float
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import declarative_base

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

class stopsTableUpdate(Base):
    __tablename__='stops_update'
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

quit()

