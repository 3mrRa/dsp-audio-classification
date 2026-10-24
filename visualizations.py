"""
visualizations.py — all plotting functions.

Covers Tasks 2, 3, 4, and the MFCC / feature-distribution plots.
Every function saves its output to PLOTS_DIR and closes the figure.
"""

import os
import numpy as np
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq

from attributes import SAMPLE_RATE, FRAME_LENGTH, HOP_LENGTH, PLOTS_DIR, N_MFCC


def _save(path):
    """Save the current matplotlib figure to disk and close it."""
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ── Task 2 ───────────────────────────────────────────────────────────────────

def plot_waveforms(real_sig, fake_sig):
    """Time-domain waveforms for one real and one fake file."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 5))
    fig.suptitle("Time-Domain Waveforms (after pre-emphasis)", fontsize=13)

    for ax, sig, title, c in zip(
            axes,
            [real_sig, fake_sig],
            ["Real Audio", "Fake Audio (AI-generated)"],
            ["steelblue", "tomato"]):
        t = np.linspace(0, len(sig) / SAMPLE_RATE, len(sig))
        ax.plot(t, sig, color=c, linewidth=0.4)
        ax.set_title(title)
        ax.set_xlabel("Time (s)")
        ax.set_ylabel("Amplitude")
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "waveforms.png"))


# ── Task 3 ───────────────────────────────────────────────────────────────────

def plot_windowing_demo(real_sig):
    """
    Four-panel figure showing WHY windowing is needed before FFT.

    Without a window the abrupt frame edges cause spectral leakage:
    energy from strong frequency components bleeds into neighbouring
    bins, corrupting the spectrum. A Hamming window tapers the frame
    smoothly to zero at both ends, suppressing this leakage.
    """
    mid = max(0, len(real_sig) // 2 - FRAME_LENGTH // 2)
    raw = real_sig[mid: mid + FRAME_LENGTH].copy()
    if len(raw) < FRAME_LENGTH:
        raw = np.pad(raw, (0, FRAME_LENGTH - len(raw)))

    win  = np.hamming(FRAME_LENGTH)
    wnd  = raw * win
    t_ms = np.arange(FRAME_LENGTH) / SAMPLE_RATE * 1000
    freq = fftfreq(FRAME_LENGTH, 1.0 / SAMPLE_RATE)[:FRAME_LENGTH // 2]
    db   = lambda x: 20 * np.log10(np.abs(fft(x))[:FRAME_LENGTH // 2] + 1e-10)

    fig, axes = plt.subplots(2, 2, figsize=(12, 6))
    fig.suptitle(
        "Framing & Windowing Demo  (25 ms frame, Hamming window)\n"
        "Why windowing is needed: suppresses spectral leakage before FFT",
        fontsize=11)

    axes[0, 0].plot(t_ms, raw, "steelblue", lw=0.8)
    axes[0, 0].set_title("Raw Frame (rectangular window)")
    axes[0, 0].set_xlabel("Time (ms)"); axes[0, 0].set_ylabel("Amplitude")
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(t_ms, wnd, "darkorange", lw=0.8)
    axes[0, 1].plot(t_ms, win * np.max(np.abs(raw)), "k--", lw=0.7,
                    alpha=0.4, label="Hamming envelope (scaled)")
    axes[0, 1].set_title("Hamming-Windowed Frame")
    axes[0, 1].set_xlabel("Time (ms)"); axes[0, 1].set_ylabel("Amplitude")
    axes[0, 1].legend(fontsize=8); axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].plot(freq, db(raw), "steelblue", lw=0.7)
    axes[1, 0].set_title("FFT of Raw Frame  -- spectral leakage visible")
    axes[1, 0].set_xlabel("Frequency (Hz)"); axes[1, 0].set_ylabel("Magnitude (dB)")
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(freq, db(wnd), "darkorange", lw=0.7)
    axes[1, 1].set_title("FFT of Windowed Frame  -- reduced leakage")
    axes[1, 1].set_xlabel("Frequency (Hz)"); axes[1, 1].set_ylabel("Magnitude (dB)")
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "windowing_demo.png"))


# ── Task 4 ───────────────────────────────────────────────────────────────────

def plot_fft(real_sig, fake_sig):
    """Single-sided FFT magnitude spectrum for one real and one fake file."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 5))
    fig.suptitle("FFT Magnitude Spectrum", fontsize=13)

    for ax, sig, title, c in zip(
            axes,
            [real_sig, fake_sig],
            ["Real Audio", "Fake Audio (AI-generated)"],
            ["steelblue", "tomato"]):
        N    = len(sig)
        spec = np.abs(fft(sig))[:N // 2]
        freq = fftfreq(N, 1.0 / SAMPLE_RATE)[:N // 2]
        ax.plot(freq, 20 * np.log10(spec + 1e-10), color=c, lw=0.6)
        ax.set_title(title)
        ax.set_xlabel("Frequency (Hz)"); ax.set_ylabel("Magnitude (dB)")
        ax.set_xlim([0, SAMPLE_RATE / 2]); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "fft_magnitude.png"))


def plot_spectrograms(real_sig, fake_sig):
    """STFT spectrograms with Hamming window, 25 ms frames, 50 % overlap."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("STFT Spectrograms  (Hamming, 25 ms, 50 % overlap)", fontsize=13)

    for ax, sig, title in zip(
            axes,
            [real_sig, fake_sig],
            ["Real Audio", "Fake Audio (AI-generated)"]):
        D    = librosa.stft(sig, n_fft=FRAME_LENGTH,
                             hop_length=HOP_LENGTH, window="hamming")
        S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
        img  = librosa.display.specshow(
            S_db, sr=SAMPLE_RATE, hop_length=HOP_LENGTH,
            x_axis="time", y_axis="hz", ax=ax, cmap="magma")
        ax.set_title(title)
        fig.colorbar(img, ax=ax, format="%+2.0f dB")

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "spectrograms.png"))


# ── Task 8 (visual) ──────────────────────────────────────────────────────────

def plot_mfcc(real_sig, fake_sig):
    """MFCC heatmaps for real vs fake -- visual part of the improvement."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    fig.suptitle("MFCC Heatmaps: Real vs Fake", fontsize=13)

    for ax, sig, title in zip(
            axes,
            [real_sig, fake_sig],
            ["Real Audio", "Fake Audio (AI-generated)"]):
        M   = librosa.feature.mfcc(y=sig, sr=SAMPLE_RATE, n_mfcc=N_MFCC,
                                    n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH)
        img = librosa.display.specshow(
            M, sr=SAMPLE_RATE, hop_length=HOP_LENGTH,
            x_axis="time", ax=ax, cmap="coolwarm")
        ax.set_title(title); ax.set_ylabel("MFCC Index")
        fig.colorbar(img, ax=ax)

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "mfcc_comparison.png"))


# ── Task 5 (visual) ──────────────────────────────────────────────────────────

def plot_feature_distributions(X, y, feature_names):
    """Box plots showing how each DSP feature differs between real and fake."""
    n    = len(feature_names)
    cols = 4
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(14, rows * 3 + 0.5))
    axes = axes.flatten()
    fig.suptitle("Feature Distributions: Real (blue) vs Fake (red)", fontsize=12)

    for i, name in enumerate(feature_names):
        ax = axes[i]
        bp = ax.boxplot(
            [X[y == 0, i], X[y == 1, i]],
            tick_labels=["Real", "Fake"],
            patch_artist=True,
            medianprops=dict(color="black", linewidth=2),
            whiskerprops=dict(linewidth=1),
            capprops=dict(linewidth=1),
        )
        for patch, c in zip(bp["boxes"], ["steelblue", "tomato"]):
            patch.set_facecolor(c); patch.set_alpha(0.65)
        ax.set_title(name, fontsize=9)
        ax.grid(True, alpha=0.3, axis="y")

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, "feature_distributions.png"))
