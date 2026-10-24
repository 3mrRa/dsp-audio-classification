"""
main.py -- DSP Audio Deepfake Detection pipeline entry point.

Run:  python main.py

Imports one function from each module and calls them in pipeline order.
All logic lives in the imported modules -- this file just orchestrates.
"""

from sklearn.model_selection import train_test_split

from attributes import PLOTS_DIR, RESULTS_DIR, FRAME_LENGTH, HOP_LENGTH, SAMPLE_RATE, FRAME_MS
from preprocessing import load_dataset
from visualizations import (plot_waveforms, plot_windowing_demo, plot_fft,
                             plot_spectrograms, plot_mfcc,
                             plot_feature_distributions)
from filters import plot_filter_analysis
from features import build_feature_matrix, NAMES_BASE, NAMES_EXT
from classification import run_classifiers, plot_feature_importance, save_results


def main():
    sep = "=" * 68
    print(sep)
    print("  DSP Audio Deepfake Detection  --  Full Pipeline")
    print(f"  Frame: {FRAME_MS} ms ({FRAME_LENGTH} samples)  |  "
          f"Hop: {HOP_LENGTH} samples (50 %)  |  SR: {SAMPLE_RATE} Hz")
    print(sep)

    # ── 1. Load & preprocess ──────────────────────────────────────────────────
    real, fake, all_ = load_dataset()
    r_sig = real[0][0]     # one real signal used for visualisations
    f_sig = fake[0][0]     # one fake signal used for visualisations

    # ── 2. Visualisations (Tasks 2, 3, 4) ────────────────────────────────────
    print("=== Visualisations ===")
    plot_waveforms(r_sig, f_sig)          # Task 2: time-domain plots
    plot_windowing_demo(r_sig)            # Task 3: why windowing is needed
    plot_fft(r_sig, f_sig)               # Task 4: FFT magnitude spectrum
    plot_spectrograms(r_sig, f_sig)      # Task 4: STFT spectrograms
    plot_mfcc(r_sig, f_sig)              # Task 8: MFCC heatmap comparison

    # ── 3. Filter design (Task 6) ─────────────────────────────────────────────
    print("\n=== Filter Design & Analysis ===")
    plot_filter_analysis()               # magnitude, phase, group delay, pole-zero

    # ── 4. Feature extraction (Task 5) ───────────────────────────────────────
    print("\n=== Feature Extraction -- Baseline (7 DSP features) ===")
    X_b, y = build_feature_matrix(all_, extended=False)
    print(f"  Matrix shape: {X_b.shape}")
    plot_feature_distributions(X_b, y, NAMES_BASE)

    print("\n=== Feature Extraction -- Extended (7 DSP + 13 MFCC) ===")
    X_e, _ = build_feature_matrix(all_, extended=True)
    print(f"  Matrix shape: {X_e.shape}")

    # ── 5. Train / test split  (same seed -> fair comparison) ────────────────
    split_kw = dict(test_size=0.2, random_state=42, stratify=y)
    Xb_tr, Xb_te, y_tr, y_te = train_test_split(X_b, y, **split_kw)
    Xe_tr, Xe_te, _,    _    = train_test_split(X_e, y, **split_kw)
    print(f"\n  Train: {len(y_tr)}  |  Test: {len(y_te)}")

    # ── 6. Baseline classifiers (Task 7) ─────────────────────────────────────
    print("\n=== Classifiers -- Baseline (7 DSP features) ===")
    base_res, dt_base = run_classifiers(Xb_tr, Xb_te, y_tr, y_te, tag="base_")
    if dt_base is not None:
        plot_feature_importance(dt_base, NAMES_BASE, tag="base")

    # ── 7. Extended classifiers (Task 8: Improvement) ────────────────────────
    print("\n=== Classifiers -- Extended (+13 MFCC)  [Task 8 Improvement] ===")
    ext_res, dt_ext = run_classifiers(Xe_tr, Xe_te, y_tr, y_te, tag="ext_")
    if dt_ext is not None:
        plot_feature_importance(dt_ext, NAMES_EXT, tag="ext")

    # ── 8. Save results table (Task 9) ────────────────────────────────────────
    print("\n=== Results Summary ===")
    save_results(base_res, ext_res)

    print(f"\n{sep}")
    print("  Pipeline complete.")
    print(f"  Plots   -> {PLOTS_DIR}/")
    print(f"  Results -> {RESULTS_DIR}/metrics.txt")
    print(sep)


if __name__ == "__main__":
    main()
