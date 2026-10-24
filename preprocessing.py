"""
preprocessing.py — audio loading and signal preprocessing.

"""

import sys
import numpy as np
import librosa

from attributes import SAMPLE_RATE, PRE_ALPHA, REAL_DIR, FAKE_DIR


def apply_preemphasis(x, alpha=PRE_ALPHA):
    """
    First-order FIR high-pass pre-emphasis filter.

    Difference equation : y[n] = x[n]  -  alpha * x[n-1]
    Transfer function   : H(z) = 1  -  alpha * z^(-1)
    Zero at z = alpha   (inside unit circle -> BIBO stable)
    Pole at z = 0       (trivial FIR pole at origin)

    Compensates for the natural -6 dB/octave spectral roll-off of
    speech, boosting high-frequency content before FFT analysis.
    """
    return np.append(x[0], x[1:] - alpha * x[:-1])


def load_audio_files(directory, label):
    """Load all .wav/.flac files from a directory, resample, normalise, pre-emphasise."""
    samples   = []
    supported = (".wav", ".flac", ".ogg", ".mp3")

    import os
    if not os.path.isdir(directory):
        print(f"  [WARN] Directory not found: {directory}")
        return samples

    files = sorted(f for f in os.listdir(directory)
                   if f.lower().endswith(supported))
    print(f"  Loading {len(files)} files from {directory} ...", flush=True)

    for fname in files:
        sig, _ = librosa.load(os.path.join(directory, fname),
                               sr=SAMPLE_RATE, mono=True)
        # Amplitude normalisation: scale peak to 1
        pk = np.max(np.abs(sig))
        if pk > 0:
            sig = sig / pk
        # Pre-emphasis
        sig = apply_preemphasis(sig)
        samples.append((sig, label))

    return samples


def load_dataset():
    """Load real (label=0) and fake (label=1) files and return both splits."""
    print("\n=== Loading dataset ===")
    real = load_audio_files(REAL_DIR, label=0)
    fake = load_audio_files(FAKE_DIR, label=1)
    all_ = real + fake
    if not all_:
        sys.exit("No audio files found. Check REAL_DIR / FAKE_DIR in attributes.py")
    print(f"  Loaded: {len(real)} real  |  {len(fake)} fake\n")
    return real, fake, all_
