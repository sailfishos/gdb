#!/bin/bash

NAME=gdb
SPECNAME=${NAME}.spec
ARCHES="armv7hl i486 x86_64 aarch64"
# If your %_vendor changes, please edit this too --cvm
VENDOR=meego
TOBASELIBS=""
TOBASELIBS_ARCH=""

for i in ${ARCHES} ; do
# cross spec files
    if [[ "${i}" =~ arm.* ]]; then
# FIXME
#	if [[ "${i}" =~ arm.*h.* ]]; then
#		CROSSTARGET=${i}-${VENDOR}-linux-gnueabihf
#	else
#
		CROSSTARGET=${i}-${VENDOR}-linux-gnueabi
#	fi
    else
	CROSSTARGET=${i}-${VENDOR}-linux-gnu
    fi
    cat ./rpm/${SPECNAME} | sed -e "s#Name: .*#Name: cross-${i}-${NAME}\n%define crosstarget ${CROSSTARGET}#" > ./rpm/cross-${i}-${NAME}.spec
done
