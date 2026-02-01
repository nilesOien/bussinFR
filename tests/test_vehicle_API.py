#!/usr/bin/env python

from fastapi.testclient import TestClient
from fastapi import status

from ..webservices.bussinAPIs import bussinApp

client=TestClient(bussinApp)

def test_response():
    response=client.get("/vehicleService")
    assert response.status_code == status.HTTP_200_OK

def test_rectangle_request():
    response=client.get("/vehicleService?minLat=-5.0&maxLat=5.0&minLon=-5.0&maxLon=5.0")

    # Did we get the right number of responses from the test database?
    assert(len(response.json()) == 11)
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

        # Did we get anything outside the lat/lon range?
        assert item.get('lat') >= -5.0
        assert item.get('lat') <= 5.0
        assert item.get('lon') >= -5.0
        assert item.get('lon') <= 5.0

