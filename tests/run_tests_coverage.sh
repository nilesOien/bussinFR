#!/bin/bash

# Turn on test mode so test databases are used
export BFR_TEST_MODE=TRUE

# Spoof an agency name
export BFR_AGENCY_NAME="Test"

# The --cov=../webservices specifies a package which in this case is that
# directory. That directory can be treated as a package
# because it has a __init__.py file (even though that file
# does nothing).

rm -rf bussinFR_coverage
uv run pytest --verbose --cov=../webservices --cov-report=html:bussinFR_coverage 

if [ -f bussinFR_coverage/index.html ]
then
 echo Success : Coverage web page top level is bussinFR_coverage/index.html
 # Put in a link so that these are served out
 cd ../webpages
 if [ ! -e bussinFR_coverage ]
 then
  ln -s ../tests/bussinFR_coverage
 fi
else
 echo There was a problem
fi

exit 0

