#!/bin/bash
#
# Shell script for managing the bluetooth connection with my Pioneer X-HM36
# Available options are:
#   - connect
#   - disconnect
#   - reconnect
#
# Script accepts only one argument at input
#
# Written by Bartosz Otlewski <botlewski@gmail.com>
#

CONNECTION_TIMEOUT=10

PIONEER_NAME="Pioneer X-HM36"
PIONEER_BD_ADDR="40:EF:4C:17:7E:F1"
PIONEER_SINK="bluez_sink.40_EF_4C_17_7E_F1.a2dp_sink"

ANALOG_PROFILE="output:analog-stereo"
ANALOG_SINK="alsa_output.pci-0000_00_1b.0.analog-stereo"

HDMI0_PORT="hdmi-output-0"
HDMI0_PROFILE="output:hdmi-stereo"
HDMI0_SINK="alsa_output.pci-0000_00_1b.0.hdmi-stereo"

HDMI1_PORT="hdmi-output-1"
HDMI1_PROFILE="output:hdmi-stereo-extra1"
HDMI1_SINK="alsa_output.pci-0000_00_1b.0.hdmi-stereo-extra1"

HDMI2_PORT="hdmi-output-2"
HDMI2_PROFILE="output:hdmi-stereo-extra2"
HDMI2_SINK="alsa_output.pci-0000_00_1b.0.hdmi-stereo-extra2"


function check_last_operation {
    if [[ $? -eq 0 ]]; then
        echo -e "\r[ OK ]"
    else
        echo -e "\r[FAIL]"
        exit 1
    fi
}


function is_pioneer_connected {
    test "$(pacmd stat | grep -i 'default sink name' | awk -F': ' '{print $2}')"  == "$PIONEER_SINK"
    echo $?
}


function connect {
    # calling sudo for output clarity
    sudo test

    # killing pulseaudio and restarting bluetooth
    echo -n "[ .. ] restarting pulseaudio and bluetooth service"
    sudo ps axo pid,command | grep -v awk | awk '/pulseaudio/ {print $1}' | sudo xargs kill -9
    sudo systemctl restart bluetooth
    check_last_operation

    # wait for bluetooth to fully restart
    sleep 1

    # connect to the pioneer
    echo -n "[ .. ] setting $PIONEER_NAME as the output device"
    echo -e "connect $PIONEER_BD_ADDR\nquit" | bluetoothctl &> /dev/null

    # wait for connection to establish
    local seconds=0
    while [[ "$(pacmd list-sinks | grep device.description | grep "$PIONEER_NAME")" == "" ]]; do
        if [[ $seconds -eq $CONNECTION_TIMEOUT ]]; then
            echo -e "\nERR: timeout reached ($CONNECTION_TIMEOUT sec)"
            exit 1
        fi
        seconds=$(($seconds + 1))
        sleep 1
    done

    # setting the default sink device
    pacmd set-default-sink $PIONEER_SINK &> /dev/null
    check_last_operation
}


function disconnect {
    # disconnect from the pioneer
    echo -n "[ .. ] disconnecting from $PIONEER_NAME"
    echo -e "disconnect $PIONEER_BD_ADDR\nquit" | bluetoothctl &> /dev/null
    check_last_operation

    local availableoutput="$(pacmd list-cards | grep hdmi-output | grep "available: yes")"

    if [[ "$(echo -e $availableoutput | grep $HDMI0_PORT)" != "" ]]; then
        echo -n "[ .. ] setting HDMI / DisplayPort as the output device"
        pacmd set-card-profile 0 $HDMI0_PROFILE &> /dev/null

        # setting the default sink
        pacmd set-default-sink $HDMI0_SINK
        check_last_operation

    elif [[ "$(echo -e $availableoutput | grep $HDMI1_PORT)" != "" ]]; then
        echo -n "[ .. ] setting HDMI / DisplayPort 2 as the output device"
        pacmd set-card-profile 0 $HDMI1_PROFILE &> /dev/null

        # setting the default sink
        pacmd set-default-sink $HDMI1_SINK
        check_last_operation

    elif [[ "$(echo -e $availableoutput | grep $HDMI2_PORT)" != "" ]]; then
        echo -n "[ .. ] setting HDMI / DisplayPort 3 as the output device"
        pacmd set-card-profile 0 $HDMI2_PROFILE &> /dev/null

        # setting the default sink
        pacmd set-default-sink $HDMI2_SINK
        check_last_operation

    else
        echo -n "[ .. ] setting built-in audio speakers as the output device"
        pacmd set-card-profile 0 $ANALOG_PROFILE &> /dev/null

        # setting the default sink
        pacmd set-default-sink $ANALOG_SINK
        check_last_operation

    fi
}


case "$1" in
connect)
    if [[ $(is_pioneer_connected) -eq 1 ]]; then
        connect
    else
        echo "$PIONEER_NAME already connected"
    fi

    ;;
disconnect)
    if [[ $(is_pioneer_connected) -eq 0 ]]; then
        disconnect
    else
        echo -e "$PIONEER_NAME not connected"
    fi

    ;;
reconnect)
    if [[ $(is_pioneer_connected) -eq 0 ]]; then
        disconnect
        sleep 1
    fi

    connect

    ;;
*)
    echo "pioneerconnect (connect|disconnect|reconnect)"
    ;;
esac
