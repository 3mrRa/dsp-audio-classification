"""
filters.py — Task 6: digital filter design and analysis.

Filter designed: Pre-emphasis FIR  H(z) = 1 - 0.97 * z^(-1)

Generates a single figure (plots/filter_analysis.png) containing:
  - Magnitude response
  - Phase response
  - Group delay
  - Pole-zero diagram
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.signal import freqz, group_delay

from attributes import PRE_ALPHA, SAMPLE_RATE, PLOTS_DIR
from visualizations import _save


def plot_filter_analysis():
    """
    Full analysis of the pre-emphasis FIR filter (Task 6).

    Difference equation : y[n] = x[n]  -  0.97 * x[n-1]
    Transfer function   : H(z) = 1  -  0.97 * z^(-1)
    Type                : 1st-order FIR (Moving Difference)
    Zero at z = 0.97    (real axis, inside unit circle -> BIBO stable)
    Pole at z = 0       (trivial FIR pole at origin)
    """
    b = np.array([1.0, -PRE_ALPHA])   # numerator coefficients
    a = np.array([1.0])               # denominator (no feedback -> FIR)

    print(f"\n  Pre-Emphasis Filter (Task 6)")
    print(f"  y[n]  =  x[n]  -  {PRE_ALPHA} * x[n-1]")
    print(f"  H(z)  =  1  -  {PRE_ALPHA} * z^(-1)")
    print(f"  Zero at z = {PRE_ALPHA}    Pole at z = 0 (trivial)")

    w,  H  = freqz(b, a, worN=1024, fs=SAMPLE_RATE)
    wg, gd = group_delay((b, a), w=1024, fs=SAMPLE_RATE)

    fig, axes = plt.subplots(2, 2, figsize=(11, 8))
    fig.suptitle(
        r"Pre-Emphasis Filter Analysis   $H(z) = 1 - 0.97\,z^{-1}$"
        "\n"
        r"Difference equation:  $y[n] = x[n] - 0.97\,x[n-1]$",
        fontsize=12)

    # Magnitude response
    axes[0, 0].plot(w, 20 * np.log10(np.abs(H) + 1e-10), "royalblue", lw=1.5)
    axes[0, 0].set_title("Magnitude Response")
    axes[0, 0].set_xlabel("Frequency (Hz)"); axes[0, 0].set_ylabel("Magnitude (dB)")
    axes[0, 0].annotate("High-freq boost\n(+6 dB/oct trend)",
                         xy=(7000, 5), fontsize=8, color="royalblue")
    axes[0, 0].grid(True, alpha=0.3)

    # Phase response
    axes[0, 1].plot(w, np.unwrap(np.angle(H)), "darkorange", lw=1.5)
    axes[0, 1].set_title("Phase Response")
    axes[0, 1].set_xlabel("Frequency (Hz)"); axes[0, 1].set_ylabel("Phase (radians)")
    axes[0, 1].grid(True, alpha=0.3)

    # Group delay
    axes[1, 0].plot(wg, gd, "seagreen", lw=1.5)
    axes[1, 0].set_title("Group Delay")
    axes[1, 0].set_xlabel("Frequency (Hz)"); axes[1, 0].set_ylabel("Samples")
    axes[1, 0].grid(True, alpha=0.3)

    # Pole-zero plot
    theta = np.linspace(0, 2 * np.pi, 300)
    zeros = np.roots(b)
    ax    = axes[1, 1]
    ax.plot(np.cos(theta), np.sin(theta), "k--", lw=0.8, alpha=0.5,
            label="Unit circle")
    ax.scatter(zeros.real, zeros.imag, marker="o", s=120,
               facecolors="none", edgecolors="royalblue", lw=2,
               label=f"Zero (z = {zeros[0]:.2f})")
    ax.scatter([0], [0], marker="x", s=120, color="tomato", lw=2,
               label="Pole (z = 0, trivial)")
    ax.axhline(0, color="k", lw=0.4); ax.axvline(0, color="k", lw=0.4)
    ax.set_xlim([-1.4, 1.4]); ax.set_ylim([-1.4, 1.4])
    ax.set_aspect("equal")
    ax.set_title("Pole-Zero Plot")
    ax.set_xlabel("Real"); ax.set_ylabel("Imaginary")
    ax.legend(fontsize=9); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "filter_analysis.png"))
