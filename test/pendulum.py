import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.integrate import solve_ivp
import time
from PyDAE._scipy.integrate._dae.dae import solve_dae, RadauDAE
from PyDAE._scipy.integrate._ivp.radau import Radau
from PyDAE._scipy.integrate._ivp.bdf import BDF


"""Cartesian pendulum, see Hairer1996 Section VII Example 2."""
m = 1
l = 1
g = 10

def F(t, vy, vyp):
    # stabilized index 1
    x, y, u, v, _, _ = vy
    x_dot, y_dot, u_dot, v_dot, la, mu = vyp

    R = np.zeros(6, dtype=np.common_type(vy, vyp))
    R[0] = x_dot - u - 2 * x * mu
    R[1] = y_dot - v - 2 * y * mu
    R[2] = m * u_dot - 2 * x * la
    R[3] = m * v_dot - 2 * y * la + m * g
    R[4] = 2 * x * u + 2 * y * v
    R[5] = x * x + y * y - l * l

    return R


def f(t, z):
    y, yp = z[:6], z[6:]
    return np.concatenate((yp, F(t, y, yp)))

diags = np.concatenate((np.ones(6), np.zeros(6)))
mass_matrix = np.diag(diags)


if __name__ == "__main__":
    # time span
    t0 = 0
    t1 = 20
    t_span = (t0, t1)

    # initial conditions
    y0 = np.array([l, 0, 0, 0, 0, 0], dtype=float)
    y_dot0 = np.array([0, 0, 0, -g, 0, 0], dtype=float)
    z0 = np.concatenate((y0, y_dot0))

    # solver options
    atol = rtol = 1e-8

    ##############
    # dae solution
    ##############
    # sol = solve_dae(F, t_span, y0, yp0, atol=atol, rtol=rtol, method=RadauDAE)
    # method = Radau
    method = BDF
    start = time.time()
    sol = solve_ivp(f, t_span, z0, atol=atol, rtol=rtol, method=method, mass_matrix=mass_matrix)
    end = time.time()
    print(f"elapsed time: {end - start}")
    t = sol.t
    y = sol.y
    success = sol.success
    status = sol.status
    message = sol.message
    print(f"success: {success}")
    print(f"status: {status}")
    print(f"message: {message}")
    print(f"nfev: {sol.nfev}")
    print(f"njev: {sol.njev}")
    print(f"nlu: {sol.nlu}")

    # visualization
    fig, ax = plt.subplots(4, 1)

    ax[0].plot(t, y[0], "-ok", label="x")
    ax[0].plot(t, y[1], "--xk", label="y")
    ax[0].legend()
    ax[0].grid()

    ax[1].plot(t, y[2], "-ok", label="u")
    ax[1].plot(t, y[3], "--xk", label="v")
    # ax[1].plot(t, y_dot[0], "-.r", label="x_dot")
    # ax[1].plot(t, y_dot[1], ":r", label="u_dot")
    ax[1].legend()
    ax[1].grid()

    # ax[2].plot(t, y_dot[2], "-k", label="u_dot")
    # ax[2].plot(t, y_dot[3], "--k", label="v_dot")
    # ax[2].legend()
    # ax[2].grid()

    # ax[3].plot(t, y[4], "-k", label="la dt")
    # ax[3].plot(t, y_dot[4], "-k", label="la")
    ax[3].plot(t, y[10], "-ok", label="la")
    ax[3].plot(t, y[11], "--xk", label="mu")
    ax[3].legend()
    ax[3].grid()

    plt.show()