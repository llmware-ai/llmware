#! /bin/bash

# This script can be used if you are developing locally directly out of this repo 
# (instead of running with a pip installed version of llmware)
# 
# It will pull the latest llmware native libraries and their dependencies

# Pull the latest wheel locally (temporarily)
cd "$(dirname "$0")"

python3 -m pip download --no-deps llmware

# Extract the right files depending on local OS
if [ "$(uname)" = "Darwin" ]; then
    unzip llmware-*.whl "llmware/.dylibs/*" "llmware/*.so" -d ../..
else
    unzip llmware-*.whl "llmware.libs/*" "llmware/*.so" -d ../..
fi

# Delete the wheel
rm llmware-*.whl