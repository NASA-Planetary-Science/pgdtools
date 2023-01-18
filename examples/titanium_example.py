"""For Benoit: Compare some Ti isotope ratios."""

from iniabu import inimf  # import as mass_fraction values right away
import matplotlib.pyplot as plt
import numpy as np

import pgdtools

# ### Deal with some model data ###
# Fake Modeldata: I assume we have mass fraction np.ndarrays of individual isotopes
# Todo: You might want to replace those next three lines with your models ;)
ti46_model = np.ones(3) * inimf.iso["Ti-46"].abu_solar * np.array([1.01, 1.05, 1.10])
ti47_model = np.ones(3) * inimf.iso["Ti-47"].abu_solar * np.array([1.01, 1.04, 1.07])
ti48_model = np.ones_like(ti46_model) * inimf.iso["Ti-48"].abu_solar  # constant
ti49_model = np.ones(3) * inimf.iso["Ti-49"].abu_solar * np.array([1.01, 1.05, 1.13])

# Now we are going to create delta values from the model data using the iniabu module
delta46ti_model = inimf.iso_delta("Ti-46", "Ti-48", ti46_model / ti48_model)
delta47ti_model = inimf.iso_delta("Ti-47", "Ti-48", ti47_model / ti48_model)
delta49ti_model = inimf.iso_delta("Ti-49", "Ti-48", ti49_model / ti48_model)

# ### Grab the grain data and work with those ###
# initialize the pgdtools - this will change probably with time
pg = pgdtools.PresolarGrains()

# let's only use Mainstream grains -> the ones from AGB stars
pg.filter_type("M")

# reject some datapoints with too large errors
# @Benoit: This is really the only one thing that I would do, otherwise, some grains
# with insane error bars also show up in the plot.
pg.filter_value(100.0, "Ti-46", "Ti-48", "<=", err=True)

# Now grab our x and y data to plot:
x_isos = ("Ti-46", "Ti-48")
y_isos47 = ("Ti-47", "Ti-48")
y_isos49 = ("Ti-49", "Ti-48")
xdat47, ydat47, xerr47, yerr47 = pg.return_ratios(x_isos, y_isos47)
xdat49, ydat49, xerr49, yerr49 = pg.return_ratios(x_isos, y_isos49)

# ### Plot ###
fig, ax = plt.subplots(1, 2)

# grains and model
ax[0].errorbar(
    xdat47,
    ydat47,
    xerr47,
    yerr47,
    "o",
    ms=3,
    mfc="w",
    linewidth=0.5,
    label="SiC M grains",
    zorder=1,
)
ax[0].plot(delta46ti_model, delta47ti_model, "s-", label="Fake model data", zorder=10)

ax[1].errorbar(
    xdat49,
    ydat49,
    xerr49,
    yerr49,
    "o",
    ms=3,
    mfc="w",
    linewidth=0.5,
    label="SiC M grains",
    zorder=1,
)
ax[1].plot(delta46ti_model, delta49ti_model, "s-", label="Fake model data", zorder=10)
# lines at zero, zero -> solar composition
for a in ax:
    xlim = a.get_xlim()
    ylim = a.get_ylim()
    a.hlines(0, xlim[0], xlim[1], linestyles="dashed", color="k", linewidth=0.5)
    a.vlines(0, ylim[0], ylim[1], linestyles="dashed", color="k", linewidth=0.5)
    a.set_xlim(xlim)
    a.set_ylim(ylim)

    # labels for axes
    a.set_xlabel("$\delta^{46}$Ti$_{48}$   (‰)")

    # aspect and layout
    a.set_aspect("equal")

# y label
ax[0].set_ylabel("$\delta^{47}$Ti$_{48}$   (‰)")
ax[1].set_ylabel("$\delta^{49}$Ti$_{48}$   (‰)")

fig.tight_layout()

# show it
fig.show()
