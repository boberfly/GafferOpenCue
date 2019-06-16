# GafferOpenCue
OpenCue Dispatcher for Gaffer

### Installing

This install will actually install pip into your Gaffer directory as well as OpenCue's
dependencies and will install into Gaffer's lib/python2.7/site-packages directory.
OpenCue and GafferOpenCue itself will be installed to whatever you set GAFFEROPENCUE to.

**In a terminal (Linux):**
```
export GAFFER_ROOT=<gaffer install path>
export GAFFEROPENCUE=<install destination>

git clone https://github.com/boberfly/GafferOpenCue.git
cd GafferOpenCue
./build.sh
```

### Runtime Instructions

Add to Gaffer extensions path:

`export GAFFER_EXTENSION_PATHS=$GAFFEROPENCUE:$GAFFER_EXTENSION_PATHS`

Run Gaffer:
`gaffer`
