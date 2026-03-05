#!/usr/bin/env python

from fastapi.testclient import TestClient
from fastapi import status

from ..webservices.bussinAPIs import bussinApp

client=TestClient(bussinApp)

def test_route_request():
    response=client.get("/vehicleService?routesCSV=bus01,Bus02,BUS03")

    # Did we get the right number of responses from the test database?
    assert(len(response.json()) == 3)
    for item in response.json() :

        # Are all the keys there?
        kys = [ 'route', 'current_status', 'timestamp', 'lat', 'lon', 'bearing' ]
        for ky in kys :
            assert ky in item

        # Are they all of the type we'd expect?
        assert isinstance(item['route'], str)
        assert isinstance(item['current_status'], int)
        assert isinstance(item['timestamp'], int)
        assert isinstance(item['lat'], float)
        assert isinstance(item['lon'], float)
        assert isinstance(item['bearing'], float)

        # Are the routes what we'd expect?
        assert item['route'] in ['BUS01', 'BUS02', 'BUS03' ]

