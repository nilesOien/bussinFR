#!/bin/bash

rm -fv *.db
uv run ./make_db.py

exit 0

