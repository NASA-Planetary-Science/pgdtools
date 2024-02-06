"""Routines to automatically classify a grain based on definitions in paper."""

from typing import Dict, Tuple, Union

import numpy as np
from scipy.special import erf


def classify_grain(
    c12_c13: Tuple[float, Union[float, Tuple[float, float]]] = None,
    n14_n15: Tuple[float, Union[float, Tuple[float, float]]] = None,
    d29si: Tuple[float, float] = None,
    d30si: Tuple[float, float] = None,
    al26_al27: Tuple[float, float] = None,
    rho_si: float = 0,
    ret_probabilities: bool = False,
) -> Union[Tuple[str, Union[str, None]], Dict[str, float]]:
    """Classify a measured grain according to the classification scheme.

    This returns either a Tuple of grain type and subtype (if `probabilities=False`,
    default case) or a dictionary of probabilities for each grain type
    (if `probabilities=True`).
    If multiple probabilities are the same for groups, the preference is given in the
    following way: M, AB, Y, Z, X, N, C, D.

    Measurement values can either be given as `(value, uncertainty)` or, in the case
    of C and N, if asymmetric uncertainties are available, as
    `(value, (uncertainty_plus, uncertainty_minus))`.

    If no uncertainties are given (as ``None`` or ``np.nan``), the uncertainty is
    assumed to be the ratio divided by 10.

    :param c12_c13: Carbon 12/13 isotopic ratio and uncertainty.
    :param n14_n15: Nitrogen 14/15 isotopic ratio and uncertainty.
    :param d29si: Silicon 29/28 isotopic ratio as delta value in permil and uncertainty.
    :param d30si: Silicon 30/28 isotopic ratio as delta value in permil and uncertainty.
    :param al26_al27: Aluminium 26/27 isotopic ratio and uncertainty.
    :param rho_si: Silicon correlation coefficient between d30Si and d29Si.
    :param ret_probabilities: Return probabilities for each grain type?
        Defaults to `False`.

    :return: Tuple of grain type and subtype or dictionary of probabilities.
    """
    # todo some checking of input data
    types = ["M", "AB", "Y", "Z", "X", "C", "N", "D"]
    probabilities = np.zeros(len(types))

    if c12_c13 is None and n14_n15 is None and d29si is None and d30si is None:
        if not ret_probabilities:
            return "U", None  # unclassified
        else:
            return dict(zip(types, probabilities))  #

    c12_c13 = _replace_errors(c12_c13)
    n14_n15 = _replace_errors(n14_n15)
    d29si = _replace_errors(d29si)
    d30si = _replace_errors(d30si)
    al26_al27 = _replace_errors(al26_al27)

    # replace no errors (None or nan) with ratio / 10

    # get elemental probabilities
    prob_al = aluminium_probabilities(al26_al27)
    prob_c = carbon_probabilities(c12_c13)
    prob_n = nitrogen_probabilities(n14_n15)
    prob_si = silicon_probabilities(d29si, d30si, rho_si)

    for it, gtype in enumerate(types):
        probabilities[it] = (
            prob_al[gtype] * prob_c[gtype] * prob_n[gtype] * prob_si[gtype]
        )

    probabilities = np.round(probabilities, 3)  # round to three significant digits
    # find maximum probability by sorting from lowest to highest.
    # preference given by numpy to first element in case of equal probabilities
    index_max = np.argsort(1 - probabilities)[0]

    if probabilities[index_max] < 0.01:
        gtype = "U"
    else:
        gtype = types[index_max]

    if gtype in ["X", "AB", "C"]:
        subtype = find_subtype(gtype, c12_c13, n14_n15, d29si, d30si)
    else:
        subtype = None

    if not ret_probabilities:
        return gtype, subtype
    else:
        return dict(zip(types, probabilities))


def aluminium_probabilities(msr: Tuple[float, float] = None) -> Dict[str, float]:
    """Calculate probabilities for aluminium isotopic data.

    :param msr: Aluminium 26/27 isotopic ratio and uncertainty.

    :return: Dictionary of probabilities for each grain type.
    """
    prob_dict = {"M": 1, "AB": 1, "Y": 1, "Z": 1, "X": 1, "N": 1, "C": 1, "D": 1}

    if msr is not None:
        prob_dict["M"] = probability_value(msr, 0.02)

        prob_dict["Y"] = prob_dict["M"]

        prob_dict["Z"] = prob_dict["M"]

        prob_dict["X"] = 0.05 + 0.95 * (1 - probability_value(msr, 0.01))

        prob_dict["C"] = prob_dict["X"]

        prob_dict["D"] = prob_dict["X"]

        prob_dict["N"] = prob_dict["X"]

        prob_dict["AB"] = 1

    return prob_dict


def carbon_probabilities(
    msr: Tuple[float, Union[float, Tuple[float, float]]] = None,
) -> Dict[str, float]:
    """Calculate probabilities for carbon isotopic data.

    :param msr: Carbon 12/13 isotopic ratio and uncertainty.

    :return: Dictionary of probabilities for each grain type.
    """
    prob_dict = {"M": 1, "AB": 0, "Y": 0, "Z": 1, "X": 1, "N": 0, "C": 1, "D": 1}

    if msr is not None:
        prob_dict["M"] = probability_value(msr, 100) - probability_value(msr, 13.5)
        prob_dict["Z"] = prob_dict["M"]
        prob_dict["Y"] = 1 - probability_value(msr, 100)
        prob_dict["AB"] = 0.8 * probability_value(msr, 13.5) + 0.2 * probability_value(
            msr, 25
        )
        prob_dict["N"] = prob_dict["AB"]

    return prob_dict


def find_subtype(
    type: str,
    c12_c13: Tuple[float, Union[float, Tuple[float, float]]],
    n14_n15: Tuple[float, Union[float, Tuple[float, float]]],
    d29si: Tuple[float, float],
    d30si: Tuple[float, float],
) -> Union[str, None]:
    """Find subtype for types X, AB or C.

    :param type: Main grain type.
    :param c12_c13: Carbon 12/13 isotopic ratio and uncertainty.
    :param n14_n15: Nitrogen 14/15 isotopic ratio and uncertainty.
    :param d29si: Silicon 29/28 isotopic ratio and uncertainty.
    :param d30si: Silicon 30/28 isotopic ratio and uncertainty.

    :return: Subtype.
    """
    if type == "X":
        if d29si is None or d30si is None:
            return None
        else:
            if d29si[0] > 30 + (2 / 3 - 0.05) * d30si[0]:
                return "X0"
            elif d29si[0] < -30 + (2 / 3 + 0.05) * d30si[0]:
                return "X2"
            else:
                return "X1"
    elif type == "AB":
        if c12_c13 is None or n14_n15 is None:
            return None
        else:
            try:
                sigma_c_plus = c12_c13[1][0]
                sigma_c_minus = c12_c13[1][1]
            except TypeError:
                sigma_c_plus = c12_c13[1]
                sigma_c_minus = c12_c13[1]
            try:
                sigma_n_plus = n14_n15[1][0]
                sigma_n_minus = n14_n15[1][1]
            except TypeError:
                sigma_n_plus = n14_n15[1]
                sigma_n_minus = n14_n15[1]
            if (
                probability_value(c12_c13, 4.5) * probability_value(n14_n15, 441)
                > (1 - probability_value(c12_c13, 4.5))
                * (1 - probability_value(n14_n15, 272))
                and c12_c13[0] - sigma_c_minus <= 4.5
                and n14_n15[0] - sigma_n_minus <= 441
            ):
                return "AB1"
            elif (
                probability_value(c12_c13, 4.5) * probability_value(n14_n15, 441)
                <= (1 - probability_value(c12_c13, 4.5))
                * (1 - probability_value(n14_n15, 272))
                and c12_c13[0] + sigma_c_plus >= 4.5
                and n14_n15[0] + sigma_n_plus >= 272
            ):
                return "AB2"
            else:
                return None
    elif type == "C":
        if c12_c13 is None:
            return None
        elif c12_c13[0] >= 10:
            return "C1"
        else:
            return "C2"


def nitrogen_probabilities(
    msr: Tuple[float, Union[float, Tuple[float, float]]] = None,
) -> Dict[str, float]:
    """Calculate probabilities for nitrogen isotopic data.

    :param msr: Nitrogen 14/15 isotopic ratio and uncertainty.

    :return: Dictionary of probabilities for each grain type.
    """
    prob_dict = {"M": 1, "AB": 1, "Y": 1, "Z": 1, "X": 1, "N": 1, "C": 1, "D": 1}

    if msr is not None:
        prob_dict["M"] = 1 - probability_value(msr, 200)
        prob_dict["Y"] = prob_dict["M"]
        prob_dict["Z"] = prob_dict["M"]
        prob_dict["X"] = probability_value(msr, 272)
        prob_dict["C"] = prob_dict["X"]
        prob_dict["D"] = prob_dict["X"]
        prob_dict["N"] = prob_dict["X"]

    return prob_dict


def probability_chi(chi: float) -> float:
    """Calculate the probability for a given chi value.

    Integrates the cumulative distribution function from minus infinity to chi for
    a normal distribution.

    :param chi: Chi-value to integrate to.

    :return: Probability for given chi value.
    """
    return 0.5 * (1 + erf(chi / np.sqrt(2)))


def probability_slope(
    xval: Tuple[float, Union[float, Tuple[float, float]]],
    yval: Tuple[float, Union[float, Tuple[float, float]]],
    comp: Tuple[float, Union[float, Tuple[float, float]]],
    rhoxy: float = 0,
) -> float:
    """Calculate the probability for a grain when compared to a line.

    :param xval: X value and uncertainty (e.g., d30Si).
    :param yval: Y value and uncertainty (e.g., d29Si).
    :param comp: Intercept and slope for the given line to compare with.
    :param rhoxy: Correlation coefficient between x and y.

    :return: Probability of measurement in comparison with given line
    """
    a, b = comp
    x, xunc = xval
    y, yunc = yval

    chi = -(y - b * x - a) / np.sqrt(
        yunc**2 + b**2 * xunc**2 - 2 * b * xunc * yunc * rhoxy
    )
    return probability_chi(chi)


def silicon_probabilities(
    msr_d29si: Tuple[float, Union[float, Tuple[float, float]]] = None,
    msr_d30si: Tuple[float, Union[float, Tuple[float, float]]] = None,
    rho: float = 0,
) -> Dict[str, float]:
    """Calculate probabilities for silicon isotopic data.

    :param msr_d29si: Silicon 29/28 isotopic ratio as delta value (permil)
        and uncertainty.
    :param msr_d30si: Silicon 30/28 isotopic ratio as delta value (permil)
        and uncertainty.
    :param rho: Correlation coefficient between d30Si and d29Si.

    :return: Dictionary of probabilities for each grain type.
    """
    # define parameters for the lines in silicon 3 isotope plot
    pm0 = (-19, 1.342)
    pm1 = (-19 + 250 * 1.342, 1.342)
    pm2 = (-19 - 100 * 1.342, 1.342)
    pm3 = (-19 + 200 * (1.342 + 1 / 1.342), -1 / 1.342)
    pm4 = (-19 - 75 * (1.342 + 1 / 1.342), -1 / 1.342)

    prob_dict = {"M": 1, "AB": 1, "Y": 1, "Z": 0, "X": 0.2, "N": 0, "C": 0, "D": 0}

    if msr_d29si is not None and msr_d30si is not None:  # values for both
        prob_dict["M"] = (
            probability_slope(msr_d30si, msr_d29si, pm1, rho)
            - probability_slope(msr_d30si, msr_d29si, pm2, rho)
        ) * (
            probability_slope(msr_d30si, msr_d29si, pm3, rho)
            - probability_slope(msr_d30si, msr_d29si, pm4, rho)
        )

        prob_dict["AB"] = prob_dict["M"]

        prob_dict["X"] = (
            probability_value(msr_d29si, 0)
            * probability_value(msr_d30si, 0)
            * (0.2 + 0.8 * probability_slope(msr_d30si, msr_d29si, pm4, rho))
        )

        prob_dict["Y"] = (
            probability_slope(msr_d30si, msr_d29si, pm1, rho)
            * (
                1
                - (1 - probability_slope(msr_d30si, msr_d29si, pm3, rho))
                * (1 - probability_value(msr_d29si, 200))
            )
            * (
                1
                - probability_slope(msr_d30si, msr_d29si, pm4, rho)
                * probability_value(msr_d30si, 0)
            )
            * (1 - probability_value(msr_d29si, -200))
        )

        prob_dict["Z"] = (
            probability_slope(msr_d30si, msr_d29si, pm2, rho)
            * (probability_value(msr_d29si, 200) - probability_value(msr_d29si, -200))
            * (1 - probability_value(msr_d30si, 0))
        )

        prob_dict["C"] = (
            (1 - probability_value(msr_d29si, 200))
            * (1 - probability_value(msr_d30si, 200))
            * (1 - probability_slope(msr_d30si, msr_d29si, pm3, rho))
        )

        prob_dict["D"] = (
            (1 - probability_value(msr_d29si, 0))
            * probability_value(msr_d30si, 200)
            * (
                1
                - 0.8 * probability_slope(msr_d30si, msr_d29si, pm1, rho)
                - 0.2 * probability_slope(msr_d30si, msr_d29si, pm0, rho)
            )
        )

        prob_dict["N"] = (
            probability_slope(msr_d30si, msr_d29si, pm2, rho)
            * probability_value(msr_d29si, 200)
            * (1 - probability_value(msr_d30si, 0))
        )
    elif msr_d29si is not None:  # only d29Si available
        prob_dict["M"] = probability_value(msr_d29si, 200) - probability_value(
            msr_d29si, -120
        )

        prob_dict["AB"] = prob_dict["M"]

        prob_dict["X"] = probability_value(msr_d29si, -120)

        prob_dict["Y"] = probability_value(msr_d29si, 200) - probability_value(
            msr_d29si, -200
        )

        prob_dict["Z"] = 0

        prob_dict["C"] = prob_dict["Z"]

        prob_dict["D"] = prob_dict["Z"]

        prob_dict["N"] = prob_dict["Z"]

    elif msr_d30si is not None:  # only d30Si available
        prob_dict["M"] = probability_value(msr_d30si, 200) - probability_value(
            msr_d30si, -100
        )

        prob_dict["AB"] = prob_dict["M"]

        prob_dict["X"] = probability_value(msr_d30si, -100)

        prob_dict["Y"] = 1 - probability_value(msr_d30si, -100)

        prob_dict["Z"] = 0

        prob_dict["C"] = prob_dict["Z"]

        prob_dict["D"] = prob_dict["Z"]

        prob_dict["N"] = prob_dict["Z"]

    return prob_dict


def probability_value(
    msr: Tuple[float, Union[float, Tuple[float, float]]], comp: float
) -> float:
    """Calculate the probability  `p(msr < comp`).

    As defined in equation (3) - (5) in the paper.

    :param msr: Measurement and uncertainty, as a Tuple.
    :param comp: Comparison value.

    :return: Probability of measurement in comparison to comparison value.
    """
    mu, sigmas = msr
    try:
        sigma_plus, sigma_minus = sigmas
        if mu < comp:
            sigma = sigma_plus
        else:
            sigma = sigma_minus
    except TypeError:  # we don't have plus, minus errors
        sigma = sigmas
    chi = (comp - mu) / sigma
    return probability_chi(chi)


def _replace_errors(
    msr: Union[float, Tuple[float, Union[float, Tuple[float, float]]], None],
) -> Union[Tuple[float, Union[float, Tuple[float, float]]], None]:
    """If no errors are given (or given as ``np.nan`` or ``None``), replace them.

    Replacement takes place with ratio / 10.

    :param msr: Measurement as float (no error), as Tuple with one or two errors,
        or None.

    :return: Measurement with errors where non-existent replaced.
    """
    if msr is None:
        return None
    elif not hasattr(msr, "__iter__"):  # no errors
        return (msr, np.abs(msr / 10))
    elif isinstance(msr, tuple):
        value, err = msr
        if hasattr(err, "__iter__"):  # two errors
            err_plus, err_minus = err
            if err_plus is None or np.isnan(err_plus):
                err_plus = np.abs(value / 10)
            if err_minus is None or np.isnan(err_minus):
                err_minus = np.abs(value / 10)
            return value, (err_plus, err_minus)
        else:  # one error
            if err is None or np.isnan(err):
                err = np.abs(value / 10)
            return value, err
