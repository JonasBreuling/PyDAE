import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import solve_ivp
from dae import BDF, Radau

def make_robertson(DAE=True):
    if DAE == True:
        mass_matrix = np.eye(3)
        mass_matrix[-1, -1] = 0
    else:
        mass_matrix = np.eye(3)

    def rhs(t, y):
        """Robertson problem of semi-stable chemical reaction, see mathworks and Shampine2005.

        References:
        -----------
        mathworks: https://de.mathworks.com/help/matlab/math/solve-differential-algebraic-equations-daes.html#bu75a7z-5 \\
        Shampine2005: https://doi.org/10.1016/j.amc.2004.12.011
        """
        y1, y2, y3 = y

        y_dot = np.zeros(3, dtype=y.dtype)
        y_dot[0] = -0.04 * y1 + 1e4 * y2 * y3
        y_dot[1] = 0.04 * y1 - 1e4 * y2 * y3 - 3e7 * y2**2
        if DAE:
            y_dot[2] = y1 + y2 + y3 - 1
        else:
            y_dot[2] = 3e7 * y2**2

        return y_dot
    
    return mass_matrix, rhs

if __name__ == "__main__":
    DAE = True

    # time span
    t0 = 0
    t1 = 1e3
    t_span = (t0, t1)

    # initial conditions
    y0 = np.array([1, 0, 0], dtype=float)

    # solver options
    atol = 5e-8
    rtol = 1e-12

    # reference solution
    mass_matrix, rhs = make_robertson(DAE=False)
    sol = solve_ivp(rhs, t_span, y0, atol=atol, rtol=rtol, method="Radau")
    t_scipy = sol.t
    y_scipy = sol.y

    # dae solution
    mass_matrix, rhs = make_robertson(DAE=DAE)
    # sol = solve_ivp(rhs, t_span, y0, atol=atol, rtol=rtol, method=BDF, mass_matrix=mass_matrix)
    sol = solve_ivp(rhs, t_span, y0, atol=atol, rtol=rtol, method=Radau, mass_matrix=mass_matrix)
    t = sol.t
    y = sol.y
    success = sol.success
    status = sol.status
    message = sol.message
    print(f"success: {success}")
    print(f"status: {status}")
    print(f"message: {message}")

    # visualization
    fig, ax = plt.subplots()

    ax.plot(t, y[0], "-ok", label="y1 BDF", mfc="none")
    ax.plot(t, y[1] * 1e4, "-ob", label="y2 BDF", mfc="none")
    ax.plot(t, y[2], "-og", label="y3 BDF", mfc="none")
    ax.plot(t_scipy, y_scipy[0], "xr", label="y1 scipy", markersize=7)
    ax.plot(t_scipy, y_scipy[1] * 1e4, "xy", label="y2 scipy", markersize=7)
    ax.plot(t_scipy, y_scipy[2], "xm", label="y3 scipy", markersize=7)
    ax.set_xscale("log")
    ax.legend()
    ax.grid()

    plt.show()
