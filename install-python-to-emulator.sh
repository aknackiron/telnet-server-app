#!/bin/bash

############################################
# 
#  Install Python and SL4A onto emulator
#
############################################

SL4A="https://android-scripting.googlecode.com/files/sl4a_r6.apk"
P4A="https://android-scripting.googlecode.com/files/PythonForAndroid_r4.apk"

function printHelp()
{
    echo "Usage: $0 [emulator or device name]"
    if [ $# -gt 0 ]
    then 
	echo "Unknown command arguments: '$@'"
	echo "Typical usage scenario is:"
	echo -e "$0 emulator-555x"
    fi
}

if [ "$#" -eq 1 ]
then 
    EMULATOR="$1"
else
    printHelp
    echo "Currently connected emulators/device:"
    adb devices -l
    exit 1
fi

# download files
SL4A_file=$(mktemp tmp.XXXX).apk
P4A_file=$(mktemp tmp.XXXX).apk

echo "Downloading SL4A"
wget --output-document="$SL4A_file" "$SL4A"

echo "Downloading Python for Android"
wget --output-document="$P4A_file" "$P4A"

# installs Python for Android apk to device/emulator
adb -s "$EMULATOR"  install "$P4A_file"

# installs SL4A apk onto device/emulator
adb -s "$EMULATOR" install "$SL4A_file"

echo "Removing downloaded files"
rm "$SL4A_file" "$P4A_file"

echo "Start Python on device and install missing modules Zope and Twisted. Then copy server file onto device."
