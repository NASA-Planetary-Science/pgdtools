# Development version of `stardustlib`

This folder contains a very rough draft /
development version /
idea gathering file(s)
for `stardustlib`.
Use at your own risk!

The idea behind this folder is to have a place
to share (really) early versions of `stardustlib`
with colleagues for testing
and feedback.
Thinks might change at any time!
There's no guarantee for consistency,
or anything, you've been warned.
That being said,
there should also be example files.
Have a look at the latest dates, etc.,
in order to find one that might work.

Feedback extremely welcome!

## Installation

### Jupyterlab server (e.g., WENDI, ...)

In the first cell of your jupyter notebook,
run the following code:

```
%pip install git+https://github.com/galactic-forensics/stardustlib.git
```

This should pull the latest version
of `stardustlib` from GitHub and install it.
To test, follow steps below.

### Local

To use this module,
clone this repository
and enter it:
```bash
git clone https://github.com/galactic-forensics/stardustlib.git
cd stardustlib
```

It is recommended that you use
a virtual python environment for the following steps.
Also: these steps have been tested with python 3.9.

First, install the python requirements,
then the package itself.
You can skip the jupyter and ipython line if you
do not want to use these tools.

```
pip install .
```

### Give it a spin

Now you should be ready to use `stardustlib`
from your session. Try the following:

```python
import stardustlib
sdl = stardustlib.StarDust()
```

If this does not throw an error,
you should be fine and the
presolar grain database was found.

## Examples

The `examples` folder contains some examples for you to read through.
There are some pure python exampmles,
as well as an ipython notebook for your consideration.
Please let me know if things are unclear, etc.

## Presolar grain database

The presolar grain database
can be found at
https://presolar.physics.wustl.edu/presolar-grain-database/.
Note that only the SiC database
is currently thought of being error free.
The current version of `stardustlib`
includes the 2021-01-10 version
of the presolar SiC grain database,
which is the current version as of this writing (Nov 2021).

## Development

To make a development installation,
type:

```python
pip install -e .[dev]
```

This will install all required packages.

More to come on this...
