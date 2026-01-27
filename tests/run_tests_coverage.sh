#!/bin/bash

# Turn on test mode so test databases are used
export BFR_TEST_MODE=TRUE

# The --cov=. specifies a package which in this case is this
# directory. This directory can be treated as a pckage
# because it has a __init__.py file (even though that file
# does nothing).

rm -rf bussinFR_coverage
uv run pytest --verbose --cov=../webservices --cov-report=html:bussinFR_coverage 

if [ -f bussinFR_coverage/index.html ]
then
 echo Success : Coverage web page top level is bussinFR_coverage/index.html
else
 echo There was a problem
fi

exit 0

