#!/bin/bash


function printHelp()
{
    echo "Usage: $0 <emulator to start>"
    if [ $# -gt 0 ]
    then 
	echo "Unknown command arguments: '$@'"
	echo "Usage is:"
	echo -e "$0 <emulator-name>"
    fi
}

if [ $# -eq 1 ]
then 
    EMULATOR=$1
else
    EMULATOR="my_dev_AVD"
    exit 1
fi

emulator -avd "$EMULATOR" &
