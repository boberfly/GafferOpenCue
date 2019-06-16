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

Additionally make an export of CUE_HOSTS that points to your cuebot farm. If it
is on the same machine, use "localhost".

`export CUE_HOSTS="localhost"`

And then run Gaffer

`gaffer`

Verify that you can connect to your cuebot farm in the Gaffer script editor:

```
import opencue
import outline
[show.name() for show in opencue.api.getShows()]
```

Which should return something like `[u'testing']`
