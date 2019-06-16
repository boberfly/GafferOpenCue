#!/usr/bin/env bash

set -e

OPENCUE_VERSION=0.2.31
OPENCUE_LOCATION=dependencies/OpenCue/working/OpenCue-$OPENCUE_VERSION

if [[ -z "${GAFFER_ROOT}" ]]; then
    echo "ERROR : GAFFER_ROOT environment variable not set"
    exit 1
fi

if [[ -z "${GAFFEROPENCUE}" ]]; then
    echo "ERROR : GAFFEROPENCUE environment variable not set"
    exit 1
fi

curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py

$GAFFER_ROOT/bin/gaffer python get-pip.py

$GAFFER_ROOT/bin/pip install -r dependencies/requirements.txt

cd dependencies
python ./build/build.py --project OpenCue --buildDir $GAFFEROPENCUE --gafferRoot $GAFFER_ROOT
cd ..

cp -r python $GAFFEROPENCUE/
cp -r startup $GAFFEROPENCUE/
cp -r LICENSE $GAFFEROPENCUE/doc/licenses/GafferOpenCue

mkdir -p $GAFFEROPENCUE_INSTALL/python/pycue
cp -r $OPENCUE_LOCATION/pycue/FileSequence $GAFFEROPENCUE/python/
cp -r $OPENCUE_LOCATION/pycue/opencue $GAFFEROPENCUE/python/
#cp -r $OPENCUE_LOCATION/pycue/tests $GAFFEROPENCUE/python/

mkdir -p $GAFFEROPENCUE_INSTALL/bin
mkdir -p $GAFFEROPENCUE_INSTALL/etc
cp -r $OPENCUE_LOCATION/pyoutline/bin/* $GAFFEROPENCUE/bin/
cp -r $OPENCUE_LOCATION/pyoutline/etc/outline.cfg $GAFFEROPENCUE/etc/
cp -r $OPENCUE_LOCATION/pyoutline/outline $GAFFEROPENCUE/python/
#cp -r $OPENCUE_LOCATION/pyoutline/tests $GAFFEROPENCUE/python/
#cp -r $OPENCUE_LOCATION/pyoutline/wrappers $GAFFEROPENCUE/python/

echo "GAFFEROPENCUE INSTALLATION COMPLETE"
