# Installation

To install the latest stable release from PyPI, simply run:

```bash
pip install pgdtools
```

To install the latest development version from GitHub, run:

```bash
pip install git+https://github.com/NASA-Planetary-Science/pgdtools.git
```

While `pgdtools` allows accessing and working with the presolar grain database,
the release itself does not include the database.
The latest database is automatically downloaded when first using the package,
however,
if you would like to work offline we recommend running the following command
in order to install the database right after installation.

```bash
python -c "from pgdtools import db; db.update()"
```

Alternatively, you can run the following commands inside your python console:

```python
from pgdtools import db
db.update()
```

More information on database management can be found [here](db.md).
