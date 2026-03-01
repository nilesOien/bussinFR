#!/bin/bash

if [ "$#" -ne 1 ]
then
 echo A URL is required
 exit -1
fi

uv run ./url_dump.py --url "$1"

exit 0

