#!/bin/bash

# Start a very simple web server on port 9000 just
# so that I can develop the code without CORS issues.
# In production this role is played by
# the web server.

python -m http.server 9000 

#
