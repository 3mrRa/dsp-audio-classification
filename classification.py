"""
classification.py -- Tasks 7 & 9: training, evaluation, and results.

Classifiers trained:
  - SVM with RBF kernel
  - KNN (k=5)
  - Logistic Regression
  - Decision Tree

Outputs per run:
  - Confusion matrix PNG for each classifier
  - Feature importance bar chart (from Decision Tree)
  - results/metrics.txt  (combined baseline vs extended table)
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score,
                             recall_score, f1_score, confusion_matrix,
                             ConfusionMatrixDisplay)

from attributes import PLOTS_DIR, RESULTS_DIR
from visualizations import _save


# ── Classifier definitions ────────────────────────────────────────────────────

def _get_classifiers():
    """Return list of (clf, name, needs_scaling) tuples."""
    return [
        (SVC(kernel="rbf", C=10, gamma="scale", random_state=42),
         "SVM (RBF)",     True),
        (KNeighborsClassifier(n_neighbors=5),
         "KNN  k=5",      True),
        (LogisticRegression(max_iter=2000, random_state=42),
         "Logistic Reg.", True),
        (DecisionTreeClassifier(max_depth=6, random_state=42),
         "Decision Tree", False),   # trees are scale-invariant
    ]


# ── Main training + evaluation function ──────────────────────────────────────

def run_classifiers(X_tr, X_te, y_tr, y_te, tag=""):
    """
    Tasks 7 & 9: train all classifiers, print metrics, save confusion matrices.

    Parameters
    ----------
    X_tr, X_te : feature matrices for train and test
    y_tr, y_te : label vectors
    tag        : filename prefix to separate baseline vs extended plots

    Returns
    -------
    results : list of metric dicts
    dt_clf  : fitted DecisionTreeClassifier (used for feature importance)
    """
    sc     = StandardScaler().fit(X_tr)
    Xtr_sc = sc.transform(X_tr)
    Xte_sc = sc.transform(X_te)

    results = []
    dt_clf  = None

    for clf, name, use_sc in _get_classifiers():
        Xtr = Xtr_sc if use_sc else X_tr
        Xte = Xte_sc if use_sc else X_te

        clf.fit(Xtr, y_tr)
        y_pred = clf.predict(Xte)

        # Metrics
        row = {
            "Classifier": name,
            "Accuracy":   accuracy_score(y_te, y_pred),
            "Precision":  precision_score(y_te, y_pred, zero_division=0),
            "Recall":     recall_score(y_te, y_pred, zero_division=0),
            "F1-Score":   f1_score(y_te, y_pred, zero_division=0),
        }
        results.append(row)

        # Confusion matrix plot
        cm   = confusion_matrix(y_te, y_pred)
        disp = ConfusionMatrixDisplay(cm, display_labels=["Real", "Fake"])
        fig, ax = plt.subplots(figsize=(4, 4))
        disp.plot(ax=ax, colorbar=False, cmap="Blues")
        ax.set_title(f"Confusion Matrix -- {name}")
        plt.tight_layout()
        safe = (tag + name).replace(" ", "_").replace("=", "").replace(".", "")
        _save(os.path.join(PLOTS_DIR, f"cm_{safe}.png"))

        print(f"  {name:18s}  Acc={row['Accuracy']:.3f}  "
              f"P={row['Precision']:.3f}  "
              f"R={row['Recall']:.3f}  "
              f"F1={row['F1-Score']:.3f}")

        if "Decision" in name:
            dt_clf = clf

    return results, dt_clf


# ── Feature importance plot ───────────────────────────────────────────────────

def plot_feature_importance(dt, feature_names, tag=""):
    """Bar chart of Decision Tree feature importances, sorted descending."""
    imp = dt.feature_importances_
    idx = np.argsort(imp)[::-1]

    fig, ax = plt.subplots(figsize=(max(8, len(feature_names) * 0.6), 4))
    ax.bar(range(len(imp)), imp[idx], color="steelblue", alpha=0.8)
    ax.set_xticks(range(len(imp)))
    ax.set_xticklabels([feature_names[i] for i in idx],
                        rotation=45, ha="right", fontsize=9)
    ax.set_title("Decision Tree Feature Importances")
    ax.set_ylabel("Importance")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    _save(os.path.join(PLOTS_DIR, f"feature_importance_{tag}.png"))


# ── Results table ─────────────────────────────────────────────────────────────

def save_results(base_res, ext_res):
    """
    Task 9: write combined metrics table to results/metrics.txt.
    Compares baseline (7 DSP) vs extended (7 DSP + 13 MFCC).
    """
    rows = (
        [{**r, "Features": "Baseline  (7 DSP)"}            for r in base_res] +
        [{**r, "Features": "Extended  (7 DSP + 13 MFCC)"}  for r in ext_res]
    )
    df = pd.DataFrame(rows)[
        ["Features", "Classifier", "Accuracy", "Precision", "Recall", "F1-Score"]
    ]

    path = os.path.join(RESULTS_DIR, "metrics.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("=" * 90 + "\n")
        f.write("  DSP AUDIO DEEPFAKE DETECTION -- PERFORMANCE METRICS\n")
        f.write("=" * 90 + "\n\n")
        f.write(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
        f.write("\n\n" + "=" * 90 + "\n")
        f.write("  Labels        : Real = 0,  Fake = 1\n")
        f.write("  Baseline feats: ZCR, STE, Centroid, Bandwidth, Rolloff, "
                "Flatness, Autocorr\n")
        f.write("  Extended feats: Baseline + MFCC-1 to MFCC-13\n")
        f.write("=" * 90 + "\n")

    print(f"\n  Saved: {path}")
    print("\n" + df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
