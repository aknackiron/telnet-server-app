#!/bin/bash 


function printHelp()
{
    echo "Usage: $0 [port number] [device/emulator name]"
    echo "<port number> is the local port to forward to device port 8123."
}

LOCAL_PORT=9999
REMOTE_PORT=8123

if [ "$#" -eq 2 ]
then 
    LOCAL_PORT="$1"
    EMULATOR="$2"
else
    printHelp
    exit 1
fi

adb -s "$EMULATOR" forward --remove-all
echo "Setting up port forwarding from local port $LOCAL_PORT to remote port $REMOTE_PORT"
adb -s "$EMULATOR" forward tcp:"$LOCAL_PORT" tcp:"$REMOTE_PORT"

