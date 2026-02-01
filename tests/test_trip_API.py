#!/usr/bin/env python

from fastapi.testclient import TestClient
from fastapi import status

from ..webservices.bussinAPIs import bussinApp

client=TestClient(bussinApp)

def test_response():
    response=client.get("/tripService")
    assert response.status_code == status.HTTP_200_OK

def test_rectangle_request():
    response=client.get("/tripService?stopID=STP01")

    # Did we get the right number of responses from the test database?
    assert(len(response.json()) == 11)
    for item in response.json() :

        # Are all the keys there?
        kys = [ 'route', 'arrivaltime' ]
        for ky in kys :
            assert ky in item

        # Are they all of the type we'd expect?
        assert isinstance(item['route'], str)
        assert isinstance(item['arrivaltime'], int)

