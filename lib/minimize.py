#!/usr/bin/env python
#-*- coding: UTF-8 -*-

from scipy import optimize, stats
from numpy import pi

import numpy as np

tau = 2 * pi

def generic_minimizer(fitness_func, initial_guess, optimizers=None):
    """
    A common interface to various minimization algorithms
    """
    
    if optimizers == None:
        optimizers = [
            optimize.fmin, # 66
            optimize.fmin_powell,
#            optimize.leastsq,
        ]

    best_result = None
    for optimizer in optimizers:
        xend = optimizer(fitness_func, initial_guess, disp=False)
        last_result = fitness_func(xend)
        if best_result is None or last_result < best_result:
            best_guess = xend
            best_result = last_result

    return best_guess


def get_paraboloid(x, y, a0, b0, a1, b1, c=0):
    """ a0 * (x - b0) ** 2 + a1 * (y - b1) ** 2 + c """
    return a0 * (x - b0) ** 2 + a1 * (y - b1) ** 2 + c


def wrapped_gradient(phase):
    rows, cols = phase.shape
    dx, dy = np.gradient(phase)
    for diff in (dx, dy):
        diff[diff < -pi / 2] += pi
        diff[diff > pi / 2] -= pi

    return dx, dy


def get_fitted_paraboloid(data):
    """
    Adjust a paraboloid to the input data using normal linear regression over
    the gradient of each dimension outline.
    This method allow us to correct a wrapped phase paraboloic deformation.
    """
    xs, ys = data.shape
    x = np.mgrid[:xs]
    y = np.mgrid[:ys]

    diff_x, diff_y = wrapped_gradient(data)
    diff_outline_x = diff_x.mean(1)
    diff_outline_y = diff_y.mean(0)

    dax, dbx, r_value, p_value, std_err = stats.linregress(x, diff_outline_x)
    day, dby, r_value, p_value, std_err = stats.linregress(y, diff_outline_y)

    ax = dax / 2 
    bx = - dbx / dax
    ay = day / 2 
    by = - dby / day
    x, y = np.mgrid[:xs, :ys]
    return get_paraboloid(x, y, ax, bx, ay, by)


def main():
    from scipy.misc import lena
    from autopipe import showimage
    x, y = np.mgrid[:512, :512]
    eye = lena()
    data = get_paraboloid(x, y, 1, 250, 3, 300, 5)
    data /= data.ptp() / 256. * 0.25
    noisy = (data + eye).astype(float)
    noisy /= noisy.ptp() / 20
    print noisy.ptp()
    noisy %= tau
    fitted = get_fitted_paraboloid(noisy)
    showimage(eye, noisy, fitted % tau, (noisy - fitted) % tau)
    return 0


if __name__ == "__main__":
    exit(main())
