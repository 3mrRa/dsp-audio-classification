
import os

SAMPLE_RATE  = 16_000                                  # Hz
FRAME_MS     = 25                                      # milliseconds per frame
FRAME_LENGTH = int(SAMPLE_RATE * FRAME_MS / 1000)     # 400 samples  (25 ms)
HOP_LENGTH   = FRAME_LENGTH // 2                       # 200 samples  (50 % overlap so nothing gets missed at edges)
PRE_ALPHA    = 0.97                                    # pre-emphasis coefficient
N_MFCC       = 13                                      # MFCC coefficients to extract
REAL_DIR     = "dataset/real"
FAKE_DIR     = "dataset/fake"
PLOTS_DIR    = "plots"
RESULTS_DIR  = "results"

os.makedirs(PLOTS_DIR,   exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)
