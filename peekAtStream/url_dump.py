#!/usr/bin/env python

# Do the imports.
from google.transit import gtfs_realtime_pb2
import requests
import argparse

# Get the URL from the url argument.
parser = argparse.ArgumentParser(description='Dump realtime transport data from a GTFS feed.')
parser.add_argument('--url', required=True, type=str, help='The URL to dump.')
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
    exit()

# Iterate over the entities and print information
print(f"There are {len(feed.entity)} entities in the feed {args.url}")

for entity in feed.entity:
    # Print different types of data based on what the entity contains
    if entity.HasField('trip_update'):
        print("\n--- Trip Update ---")
        print(f"Entity ID: {entity.id}")
        print(f"Trip ID: {entity.trip_update.trip.trip_id}")
        print(f"Route ID: {entity.trip_update.trip.route_id}")
        for stop_time_update in entity.trip_update.stop_time_update:
            print(f"  Stop ID: {stop_time_update.stop_id}, Arrival time (Unix): {stop_time_update.arrival.time}")
        print(entity.trip_update)

    elif entity.HasField('vehicle'):
        print("\n--- Vehicle Position ---")
        print(f"Entity ID: {entity.id}")
        print(f"Latitude: {entity.vehicle.position.latitude}")
        print(f"Longitude: {entity.vehicle.position.longitude}")
        print(entity.vehicle)

    elif entity.HasField('alert'):
        print("\n--- Service Alert ---")
        print(f"Entity ID: {entity.id}")
        # Process alert details as needed
        print(entity.alert.header_text.translation[0].text)
        print(entity.alert)

