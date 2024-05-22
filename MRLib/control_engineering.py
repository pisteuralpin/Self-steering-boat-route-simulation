# ---------------------------------------------------------------------------- #
#                          Control Engineering Module                          #
#                               Mathurin Roulier                               #
# ---------------------------------------------------------------------------- #

import numpy as np
import matplotlib.pyplot as plt

# ---------------------------- Transfer functions ---------------------------- #

def transfer_function(num: list, den: list, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of a system.
    num: list of the numerator coefficients, decreasing order
    den: list of the denominator coefficients, decreasing order
    w: list of the pulsations to compute the transfer function
    """

    H = np.poly1d(num) / np.poly1d(den)
    return H(w)

# -------------------------------- Correctors -------------------------------- #

def proportional(K: float, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of a proportional corrector.
    K: proportional gain
    w: list of the pulsations to compute the transfer function
    """

    return K * np.ones(len(w))

def integral(K: float, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of an integral corrector.
    K: integral gain
    w: list of the pulsations to compute the transfer function
    """

    return K / (1j * w)

def derivative(K: float, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of a derivative corrector.
    K: derivative gain
    w: list of the pulsations to compute the transfer function
    """

    return 1j * K * w

def proportional_integral(Kp: float, Ki: float, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of a proportional-integral corrector.
    Kp: proportional gain
    Ki: integral gain
    w: list of the pulsations to compute the transfer function
    """

    return Kp * (1 + 1j * w / Ki) / w

def proportional_derivative(Kp: float, Kd: float, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of a proportional-derivative corrector.
    Kp: proportional gain
    Kd: derivative gain
    w: list of the pulsations to compute the transfer function
    """

    return Kp * (1 + 1j * w * Kd) / w

def proportional_integral_derivative(Kp: float, Ki: float, Kd: float, w: np.ndarray) -> np.ndarray:
    """Compute the transfer function of a proportional-integral-derivative corrector.
    Kp: proportional gain
    Ki: integral gain
    Kd: derivative gain
    w: list of the pulsations to compute the transfer function
    """

    return Kp * (1 + 1j * w * Kd + 1j * w / Ki) / w


# --------------------------------- Bode plot -------------------------------- #

def bode_bode(H: callable, w1: float, w2: float):
    w = np.logspace(w1, w2, 1000)

    plt.figure()
    plt.subplot(2,1,1)
    plt.title("Bode plot")
    plt.loglog(w, np.abs(H(w)))
    plt.ylabel("Magnitude (dB)")
    plt.grid(True, which="both")
    plt.subplot(2,1,2)
    plt.semilogx(w, np.angle(H(w)))
    plt.xlabel("Frequency (rad/s)")
    plt.ylabel("Phase (rad)")
    plt.grid(True, which="both")
    plt.show()