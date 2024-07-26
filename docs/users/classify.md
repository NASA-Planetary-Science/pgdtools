We implemented the classification scheme of
[Stephan et al. (2024)](https://doi.org/10.3847/1538-4365/ad1102)
to allow the user to classify their own grain data.
Details on the actual method can be found
[in the respective API documentation](../api/classify.md).

## Example for C, N, Si isotope measurements.

Let us assume you have measured a grain with the following isotopic ratios:

- $^{12}\mathrm{C}/^{13}\mathrm{C} = 52.3^{+1.3}_{-0.7}$
- $^{14}\mathrm{N}/^{15}\mathrm{N} = 123.4^{+2.1}_{-1.3}$
- $\delta(^{29}\mathrm{Si}/^{28}\mathrm{Si}) = 12.3 \pm 0.7$
- $\delta(^{30}\mathrm{Si}/^{28}\mathrm{Si}) = 0.3 \pm 1.5$

Using `pgdtools`, you can classify this grain as following:

```python
from pgdtools import classify_sic_grain

# Define the isotopic ratios
c12c13 = (252.3, (1.3, 0.7))
n14n15 = (1023.4, (2.1, 1.3))
dsi29si28 = (12.3, 0.7)
dsi30si28 = (0.3, 1.5)

# Classify the grain
classification = classify_sic_grain(c12c13, n14n15, dsi29si28, dsi30si28)
```

This grain would be classified as `('Y', None)`, i.e., a Y grain without a subtype.
