#!/bin/bash

# Turn on test mode so test databases are used
export BFR_TEST_MODE=TRUE

# Spoof an agency name
export BFR_AGENCY_NAME="Test"

uv run pytest --verbose

