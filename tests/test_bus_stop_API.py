#!/usr/bin/env python

from fastapi.testclient import TestClient
from fastapi import status

bussinAPIs:bussinApp

from ..webservices.bussinAPIs import bussinApp

client=TestClient(bussinApp)

def test_response():
    response=client.get("/busStopService")
    assert response.status_code == status.HTTP_200_OK

def test_rectangle_request():
    response=client.get("/busStopService?minLat=-5.0&maxLat=5.0&minLon=-5.0&maxLon=5.0")

    # Did we get the right number of responses from the test database?
    assert(len(response.json()) == 11)
    for item in response.json() :

        # Are all the keys there?
        assert 'stopid' in item
        assert 'stopname' in item
        assert 'stopdesc' in item
        assert 'lat' in item
        assert 'lon' in item

        # Are they all of the type we'de expect?
        assert type(item.get('stopid') is str)
        assert type(item.get('stopname') is str)
        assert type(item.get('stopdesc') is str)
        assert type(item.get('lat') is float)
        assert type(item.get('stopid') is float)

        # Did we get anything outside the lat/lon range?
        assert item.get('lat') >= -5.0
        assert item.get('lat') <= 5.0
        assert item.get('lon') >= -5.0
        assert item.get('lon') <= 5.0

def test_range_request():
    response=client.get("/busStopService?centerLon=0.0&centerLat=0.0&rangeKm=250.0")

    # Did we get the right number of responses from the test database?
    assert(len(response.json()) == 5)
    for item in response.json() :

        # Are all the keys there?
        assert 'stopid' in item
        assert 'stopname' in item
        assert 'stopdesc' in item
        assert 'lat' in item
        assert 'lon' in item

        # Are they all of the type we'de expect?
        assert type(item.get('stopid') is str)
        assert type(item.get('stopname') is str)
        assert type(item.get('stopdesc') is str)
        assert type(item.get('lat') is float)
        assert type(item.get('stopid') is float)

        # Did we get anything outside the lat/lon range?
        assert item.get('lat') >= -2.0
        assert item.get('lat') <= 2.0
        assert item.get('lon') >= -2.0
        assert item.get('lon') <= 2.0


