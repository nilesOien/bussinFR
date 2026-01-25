#!/bin/bash

# Clean up runtime files. After this, the database will
# have to be reinitialized.

rm -vf database.db
rm -vrf fromAgency
rm -vf updated.time

exit 0
