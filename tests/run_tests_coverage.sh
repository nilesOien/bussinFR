#!/bin/bash

# Link in the config file
if [ ! -e config.json ]
then
 ln -s ../webservices/config.json
fi

# Turn on test mode so test databases are used
export BFR_TEST_MODE=TRUE

# The --cov=../webservices specifies a package which in this case is that
# directory. That directory can be treated as a package
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

