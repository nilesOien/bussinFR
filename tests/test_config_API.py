#!/usr/bin/env python

from fastapi.testclient import TestClient
from fastapi import status

from ..webservices.bussinAPIs import bussinApp

client=TestClient(bussinApp)

def test_response():
    response=client.get("/configService")
    assert response.status_code == status.HTTP_200_OK

def test_request():
    response=client.get("/configService")

    assert(isinstance(response.json(), dict))

    # Are all the keys there?
    kys = [ 'initZoom', 'maxZoom', 'minZoom', 'tabTitle',
            'title', 'mapLat', 'mapLon', 'metric', 'deviceLocation' ]
    for ky in kys :
        assert ky in response.json()

