The presolar grain class is the meat of `pgdtools` and likely the class you will use the most.
There are two ways to get the full database:

```python
from pgdtools import PresolarGrains
pgd = PresolarGrains()
```

or

```python
from pgdtools import pgd
```

We recommend the latter method, as it is shorter.

Examples for usage can be found in the Examples menu on the left.

## Filtering

One of the main features of `pgdtools` is that it allows you to filter the database.
Details on all the possible filters can be found
[here](../api/subtools.md#pgdtools.sub_tools.filters.Filters).

The following would filter the database to only show Graphite grains that have <sup>12</sup>C/<sup>13</sup>C ratios
greater than 100
and uncertainties on these ratios of less than 1.0.

```python
from pgdtools import pgd

ratio = ("12C", "13C")  # let's define the ratio once

pgd.filter.db(pgd.DataBase.Graphite)
pgd.filter.ratio(ratio, "<", 100)
pgd.filter.uncertainty(ratio, "<", 1.0)
```

At any point, you can reset the database to incldue all grains and start over.
To do so, use `pgd.reset()`.

## Data retrieval

After filtering, you might want to retreive the data.
Details on all the possible data retrieval methods can be found
[here](../api/subtools.md#pgdtools.sub_tools.data.Data).

As an example, let's say you want to plot the
<sup>12</sup>C/<sup>13</sup>C versus the
<sup>14</sup>N/<sup>15</sup>N ratios
of the grains you have filtered.

```python
from pgdtools import pgd

x_ratio = ("12C", "13C")
y_ratio = ("14N", "15N")

# do your filtering here

xdat, xunc, ydat, yunc, corr = pgd.data.ratio_xy(x_ratio, y_ratio)
```

If you only want to retrieve the data for one isotope ratios (plus the uncertainties),
check out the routine `pgd.data.ratio(...)`.

## Formatting helper functions

In order to create beautiful plots, `pgdtools` provides a few helper functions.
As you have seen above, a ratio tuple is all you need to get an isotopic ratio or a delta-value of an isotopic ratio
from the data retrieval functions.
You can use the same tuple to directly get a nicely formatted label for your plot!

```python
from pgdtools import pgd

ratio = ("12C", "13C")
label = pgd.format.ratio(ratio)
```

This will provide you with a LaTeX formatted string that you can,
e.g., directly pass to `matplotlib` as an axis label.

## References

If you are using `pgdtools` for a publication,
you might want to know who measured the original data.
We provide easy access to the references with the `pgd.reference` property.
This will act on your filtered database.
A full list of properties and methods can be found
[here](../api/subtools.md#pgdtools.sub_tools.references.References).
You can, e.g., print this property directly or just get the DOIs of the references.

```python
from pgdtools import pgd

# do your filtering here

dois = pgd.reference.doi
```

This will return a set of DOIs that you can use further, i.e., to import into your reference manager.

## Techniques

Similar to the references, `pgdtools` exposes the techniques section of the database to the user.
A full list of features can be found
[here](../api/subtools.md#pgdtools.sub_tools.techniques.Techniques).

As an example, you can get a dataframe with a set of all the techniques used for your filtered dataset:

```python
from pgdtools import pgd

# do your filtering here

techniques = pgd.techniques.table_set
```

## Information

Finally, `pgdtools` also comes with an `info` property that allows you to search the database.
While the properties `technique` and `reference` also provide you with information,
these two sections are actual tables/sheets in the Excel version of the database.
The `info` property on the other hand lets you explore the database and allows you,
e.g., to find isotope ratios that are available in the database itself.
Details on all the functionality can be found
[here](../api/subtools.md#pgdtools.sub_tools.info.Info).

As an example, let's say you want to find out what Ru isotopic ratios are available in the database:

```python
from pgdtools import pgd

av_ratios = pgd.info.ratios("Ru")
```

This will print out all the Ru isotopic ratios, but also return a list of tuples
in which you find first the ratio header and second if this ratio is a delta value.
The printed information, as an example, is as following:

```
Isotope ratios containing Ru:
- d(96Ru/100Ru), delta value: True
- d(98Ru/100Ru), delta value: True
- d(99Ru/100Ru), delta value: True
- d(101Ru/100Ru), delta value: True
- d(102Ru/100Ru), delta value: True
- d(104Ru/100Ru), delta value: True
```
