#!/bin/bash
#
# Script for simpler RW remounting of NTFS drives under MacOS system.
# Requires the ntfs-3g package.
#
# Copyright (C) 2019-2020 _kodokami
#

NTFS_DRIVES=$(diskutil list | egrep '^.*(Microsoft|Windows).*disk[1-9]s[1-9]$' | rev | cut -d' ' -f1 | rev)

function print_help {
    echo -e "Script for simpler RW remounting of NTFS drives under MacOS system."
    echo -e "Requires the ntfs-3g package.\n"
    echo -e "usage: ntfs-remount command [option]"
    echo -e "available commands:"
    echo -e "\tlist     - lists all available NTFS drives"
    echo -e "\tremount  - remounts specified drive (pass ALL for remounting all detected drives)"
    echo -e "\thelp     - prints this help message"
}

function list_drives {
    if [[ "${NTFS_DRIVES}" != "" ]]; then
        echo "Detected $(echo \"${NTFS_DRIVES}\" | wc -l | tr -d ' ') NTFS drive(s):"
        echo -en "\t" && echo -n "${NTFS_DRIVES}" | tr '\n' '-' | sed 's/-/, /g' && echo ''
    else
        echo "No NTFS drives detected"
    fi
}

function remount_drive {
    DRIVE_NAME=${1:?"err: drive name not provided"}
    DRIVE_PATH=$(mount | grep ${DRIVE_NAME} | cut -d' ' -f1)

    echo "Remounting drive ${DRIVE_NAME} mounted at $(mount | grep ${DRIVE_NAME} | cut -d' ' -f3)"

    sudo umount ${DRIVE_PATH}

    # checking for /Volumes/NTFS directory
    BASE_PATH="/Volumes/NTFS"
    if [[ ! -d $BASE_PATH ]]; then
        echo -e "Directory ${BASE_PATH} does not exists - creating it..."
        sudo mkdir -p $BASE_PATH
    fi

    X=0
    NEW_PATH=
    while true; do
        # looking for new, avilable mount point under /Volumes/NTFS/
        NEW_PATH="${BASE_PATH}/$X"
        if [[ "$(mount | grep ${NEW_PATH})" == "" ]]; then
            break
        else
            X=$(( $X + 1 ))
        fi
    done

    if [[ ! -d ${NEW_PATH} ]]; then
        echo -e "Creating directory ${NEW_PATH}"
        sudo mkdir -p ${NEW_PATH}
    fi

    EXIT_CODE=
    sudo ntfs-3g ${DRIVE_PATH} ${NEW_PATH} -olocal,oallow_other,auto_xattr && EXIT_CODE=$?

    if [[ "${EXIT_CODE}" -eq "0" ]]; then
        echo -e "Drive ${DRIVE_NAME} mounted SUCCESSFULLY!"
        echo -e "New mount point: ${NEW_PATH}"
    else
        echo -e "Mounting drive ${DRIVE_NAME} FAILED!"
    fi

    # returning ntfs-3g exit_code
    return ${EXIT_CODE}
}

function remount_all {
    SUCCESS_COUNT=0
    FAIL_COUNT=0

    if [[ "$NTFS_DRIVES" == "" ]]; then
        echo -e "No NTFS drives found"
        exit 0
    fi

    while read drive_name; do
        remount_drive ${drive_name}

        EXIT_CODE=$?
        if [[ "${EXIT_CODE}" -eq "0" ]]; then
            SUCCESS_COUNT=$(( ${SUCCESS_COUNT} + 1 ))
        else
            FAIL_COUNT=$(( ${FAIL_COUNT} + 1))
        fi

    done <<< ${NTFS_DRIVES}

    echo -en "\n${SUCCESS_COUNT} drive(s) successfully mounted [osxfuse, local, read-write]\n"
    echo -en "${FAIL_COUNT} drive(s) failed to mount\n\n"
}

function remount {
    TARGET=${1:-""}

    if [[ "$TARGET" == "" ]]; then
        echo -e "No remount target specified, type help for more information"

    elif [[ "$TARGET" == "ALL" || "$TARGET" == "all" ]]; then
        remount_all

    elif [[ $(echo ${NTFS_DRIVES} | grep $TARGET) != "" ]]; then
        remount_drive $TARGET

    else
        echo -e "$TARGET is not an NTFS drive"

    fi
}

##############
# MAIN BODY

COMMAND=${1:-""}
OPTION=${2:-""}

case $COMMAND in
    list)
        list_drives
        ;;
    remount)
        remount $OPTION
        ;;
    help)
        print_help
        ;;
    "")
        echo "No command specified, type help for more information"
        ;;
    *)
        echo "Unknown command $COMMAND, type help for more information"
        ;;
esac
