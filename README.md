[![PyPi](https://img.shields.io/pypi/v/pgdtools?color=informational)](https://pypi.org/project/pgdtools/)
[![docs](https://readthedocs.org/projects/pgdtools/badge/?version=latest)](https://pgdtools.readthedocs.io)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://github.com/NASA-Planetary-Science/pgdtools/blob/main/LICENSE)
[![tests](https://github.com/NASA-Planetary-Science/pgdtools/actions/workflows/tests.yml/badge.svg)](https://github.com/NASA-Planetary-Science/pgdtools/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/NASA-Planetary-Science/pgdtools/branch/main/graph/badge.svg?token=N0NNVEI8CX)](https://codecov.io/gh/NASA-Planetary-Science/pgdtools)
[![Rye](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/rye/main/artwork/badge.json)](https://rye.astral.sh)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)

# Presolar grain database tools (pgdTools)

Currently under development.

This folder contains a very rough draft /
development version /
idea gathering file(s)
for `pgdtools`.
Use at your own risk!

The idea behind this folder is to have a place
to share (really) early versions of `pgdtools`
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
%pip install git+https://github.com/galactic-forensics/pgdtools.git
```

This should pull the latest version
of `pgdtools` from GitHub and install it.
To test, follow steps below.

### Local

To use this module,
clone this repository
and enter it:
```bash
git clone https://github.com/galactic-forensics/pgdtools.git
cd pgdtools
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

Now you should be ready to use `pgdtools`
from your session. Try the following:

```python
import pgdtools

pg = pgdtools.PresolarGrains()
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
The current version of `pgdtools`
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
