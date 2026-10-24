"""
features.py — Task 5: DSP feature extraction.

Baseline (7 features):
  1. Zero-Crossing Rate
  2. Short-Time Energy
  3. Spectral Centroid
  4. Spectral Bandwidth
  5. Spectral Rolloff
  6. Spectral Flatness
  7. Autocorrelation Peak

Extended (20 features = baseline + 13 MFCC means):
  Added for Task 8 (Improvement) -- reproduces Alzantot et al. 2019 pipeline.
"""

import numpy as np
import librosa

from attributes import SAMPLE_RATE, FRAME_LENGTH, HOP_LENGTH, N_MFCC


# ── Feature name lists (used by classification.py and visualizations.py) ─────

NAMES_BASE = [
    "ZCR", "STE", "Spec. Centroid", "Spec. Bandwidth",
    "Spec. Rolloff", "Spec. Flatness", "Autocorr Peak",
]

NAMES_EXT = NAMES_BASE + [f"MFCC-{i+1}" for i in range(N_MFCC)]


# ── Private helpers ───────────────────────────────────────────────────────────

def _short_time_energy(signal):
    """
    STE[m] = sum of x^2[n] for each frame m.
    Captures loudness / energy variation over time.
    """
    n = 1 + (len(signal) - FRAME_LENGTH) // HOP_LENGTH
    return np.array([
        np.sum(signal[i * HOP_LENGTH: i * HOP_LENGTH + FRAME_LENGTH] ** 2)
        for i in range(n)
    ])


def _autocorr_peak(signal):
    """
    Normalised autocorrelation peak at lag > 0.

    r[tau] = sum( x[n] * x[n+tau] ) / r[0]

    Periodic (voiced) speech has a strong peak; AI-synthesised audio
    may show different periodicity characteristics.
    """
    n = 1 + (len(signal) - FRAME_LENGTH) // HOP_LENGTH
    peaks = []
    for i in range(n):
        f    = signal[i * HOP_LENGTH: i * HOP_LENGTH + FRAME_LENGTH]
        corr = np.correlate(f, f, "full")[len(f) - 1:]
        if corr[0] > 0:
            corr = corr / corr[0]
        peaks.append(float(np.max(corr[1:])) if len(corr) > 1 else 0.0)
    return np.array(peaks)


# ── Public extractors ─────────────────────────────────────────────────────────

def extract_dsp_features(signal):
    """
    Task 5 -- extract 7 DSP features and average across frames.

    Returns a 1-D array of shape (7,).

    Feature equations:
      ZCR     : (1/N) * sum |sgn(x[n]) - sgn(x[n-1])|
      STE     : sum x^2[n]  per frame
      Centroid: C  = sum(f * |X[f]|) / sum(|X[f]|)
      Bandwidth: BW = sqrt( sum((f-C)^2 * |X[f]|) / sum(|X[f]|) )
      Rolloff : freq where cumulative energy = 85 % of total
      Flatness: geometric_mean(|X[f]|) / arithmetic_mean(|X[f]|)
      Autocorr: peak of normalised autocorrelation at lag > 0
    """
    kw = dict(n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH)
    return np.array([
        np.mean(librosa.feature.zero_crossing_rate(
                    signal, frame_length=FRAME_LENGTH,
                    hop_length=HOP_LENGTH)[0]),
        np.mean(_short_time_energy(signal)),
        np.mean(librosa.feature.spectral_centroid(
                    y=signal, sr=SAMPLE_RATE, **kw)[0]),
        np.mean(librosa.feature.spectral_bandwidth(
                    y=signal, sr=SAMPLE_RATE, **kw)[0]),
        np.mean(librosa.feature.spectral_rolloff(
                    y=signal, sr=SAMPLE_RATE, **kw)[0]),
        np.mean(librosa.feature.spectral_flatness(
                    y=signal, **kw)[0]),
        np.mean(_autocorr_peak(signal)),
    ])


def extract_mfcc_features(signal):
    """
    Task 8 (Improvement) -- 13 MFCC coefficient means.

    Reproduces the MFCC pipeline from Alzantot et al. 2019:
      STFT  ->  Mel filterbank  ->  log  ->  DCT  ->  first 13 coefficients

    Returns a 1-D array of shape (13,).
    """
    M = librosa.feature.mfcc(y=signal, sr=SAMPLE_RATE, n_mfcc=N_MFCC,
                               n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH)
    return np.mean(M, axis=1)


def build_feature_matrix(all_samples, extended=False):
    """
    Run feature extraction on every (signal, label) pair.

    Parameters
    ----------
    all_samples : list of (np.ndarray, int)
    extended    : if True, append 13 MFCC means to the 7 DSP features

    Returns
    -------
    X : np.ndarray  shape (n_samples, 7 or 20)
    y : np.ndarray  shape (n_samples,)
    """
    X, y  = [], []
    total = len(all_samples)

    for idx, (sig, label) in enumerate(all_samples):
        f = extract_dsp_features(sig)
        if extended:
            f = np.concatenate([f, extract_mfcc_features(sig)])
        X.append(f)
        y.append(label)
        if (idx + 1) % 100 == 0 or (idx + 1) == total:
            print(f"    {idx+1}/{total}", end="\r", flush=True)

    print()
    return np.array(X), np.array(y)
