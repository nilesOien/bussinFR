# Database of bus stops

This creates and updates a database of bus stops :
```
./dbUpdate.sh $HOME/bussinFR/environment.vars
```

The following environment variables from the environment.vars file are used :
```
# The top level dir.
export BFR_TOP_DIR="$HOME/bussinFR"

# The URL for the station zip file that the agency publishes.
export BFR_STOPS_ZIP_URL="https://www.rtd-denver.com/files/gtfs/bustang-co-us.zip"

# When that zip file is downloaded and unzipped, this is the name of the station file
# relative to where it was unzipped.
export BFR_STOPS_FILE="stops.txt"
```

The python files are as follows :
```
init_db.py   --- Initializes the database (creates tables)
update_db.py --- Updates the table
```

If the file ```db_offline.marker``` is in this directory, then the
database is being updated and should not be read. Clients will have
to sleep until the file is removed.

The database looks like this :
```
CREATE TABLE stops (
	stopid VARCHAR NOT NULL, 
	stopname VARCHAR NOT NULL, 
	stopdesc VARCHAR NOT NULL, 
	lat FLOAT NOT NULL, 
	lon FLOAT NOT NULL, 
	PRIMARY KEY (stopid), 
	CONSTRAINT unique_constraint UNIQUE (stopid)
);
sqlite> select * from stops limit 5;
34385|Wewatta St & 17th St|Vehicles Travelling Northeast|39.754143|-105.001356
26188|Arapahoe at Village Center Station Gate D|Vehicles Travelling East|39.601134|-104.887857
35451|A Basin|Vehicles Travelling East|39.642721|-105.871835
35176|West Glenwood Park & Ride|Vehicles Travelling North|39.557502|-107.353704
35471|Wooly Mammoth Park & Ride|Vehicles Travelling South|39.697713|-105.207457
```

