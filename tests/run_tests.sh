#!/bin/bash

# Link in the config file
if [ ! -e config.json ]
then
 ln -s ../webservices/config.json
fi

# Turn on test mode so test databases are used
export BFR_TEST_MODE=TRUE

uv run pytest --verbose

