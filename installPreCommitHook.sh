#!/bin/bash

cd .git/hooks/
ln -sf ../../preCommitHook.sh pre-commit

exit 0

