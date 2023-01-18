"""For Benoit: Compare some Si isotope ratios."""

from iniabu import inimf  # import as mass_fraction values right away
import matplotlib.pyplot as plt
import numpy as np

import pgdtools

# ### Deal with some model data ###
# Fake Modeldata: I assume we have mass fraction np.ndarrays of individual isotopes
# Todo: You might want to replace those next three lines with your models ;)
si29_model = np.array(
    [3.69349323e-05, 3.73042816e-05, 3.76736309e-05, 3.80429803e-05, 3.84123296e-05]
)
si30_model = np.array(
    [2.52258297e-05, 2.57328689e-05, 2.62449532e-05, 2.67620827e-05, 2.72842574e-05]
)
si28_model = np.ones_like(si29_model) * 0.0007025488555770814  # just n times Si-28 abu

# Now we are going to create delta values from the model data using the iniabu module
delta29si_model = inimf.iso_delta("Si-29", "Si-28", si29_model / si28_model)
delta30si_model = inimf.iso_delta("Si-30", "Si-28", si30_model / si28_model)

# ### Grab the grain data and work with those ###
# initialize the pgdtools - this will change probably with time
pg = pgdtools.PresolarGrains()

# let's only use Mainstream grains -> the ones from AGB stars
pg.filter_type("M")

# let's limit ourselves to measurements with Si isotopes with <10 permil uncertainties
# Note: These data are already in delta-notation
pg.filter_value(10.0, "Si-29", "Si-28", "<=", err=True)
pg.filter_value(10.0, "Si-30", "Si-28", "<=", err=True)

# Now grab our x and y data to plot:
x_isos = ("Si-30", "Si-28")
y_isos = ("Si-29", "Si-28")
xdat, ydat, xerr, yerr = pg.return_ratios(x_isos, y_isos)

# ### Plot ###
fig, ax = plt.subplots(1, 1)

# grains and model
ax.errorbar(
    xdat,
    ydat,
    xerr,
    yerr,
    "o",
    ms=3,
    mfc="w",
    linewidth=0.5,
    label="SiC M grains",
    zorder=1,
)
ax.plot(delta30si_model, delta29si_model, "s-", label="Fake model data", zorder=10)

# lines at zero, zero -> solar composition
xlim = ax.get_xlim()
ylim = ax.get_ylim()
ax.hlines(0, xlim[0], xlim[1], linestyles="dashed", color="k", linewidth=0.5)
ax.vlines(0, ylim[0], ylim[1], linestyles="dashed", color="k", linewidth=0.5)
ax.set_xlim(xlim)
ax.set_ylim(ylim)

# labels for axes
ax.set_xlabel("$\delta^{30}$Si$_{28}$   (‰)")
ax.set_ylabel("$\delta^{29}$Si$_{28}$   (‰)")
ax.legend()

# aspect and layout
ax.set_aspect("equal")
fig.tight_layout()

# show it
fig.show()
