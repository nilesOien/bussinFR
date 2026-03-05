#!/bin/bash

if [ ! -e .git/hooks/pre-commit ]
then
 cd .git/hooks/
 ln -sf ../../preCommitHook.sh pre-commit
 echo Pre commit hook installed
else
 echo Pre commit hook already in place
fi

exit 0

