#!/usr/bin/env bash
#
# this fixes package name="." in coverage.xml  :/

set -euo pipefail

failures=0
trap 'failures=$((failures+1))' ERR

COV_FILE=${1:-coverage.xml}
VERBOSE="false"  # set to "true" for extra output

REAL_NAME=$(grep ^name setup.cfg | cut -d" " -f3)
NAME_CHECK=$(grep -o 'name="."' "${COV_FILE}")

[[ -n $NAME_CHECK ]] && sed -i -e "s|name=\".\"|name=\"${REAL_NAME}\"|" $COV_FILE

if ((failures == 0)); then
    echo "Success"
else
    echo "Something went wrong"
    exit 1
fi
