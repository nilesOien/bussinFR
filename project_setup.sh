#!/bin/bash

# Set up python env with the modules we need.

uv init --name bussinFR --description "GTFS near real time display system" --bare .
uv add -r requirements.in

