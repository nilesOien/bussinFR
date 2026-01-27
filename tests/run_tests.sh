#!/bin/bash

# Turn on test mode so test databases are used
export BFR_TEST_MODE=TRUE

uv run pytest --verbose

exit 0

