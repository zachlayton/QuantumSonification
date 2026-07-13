from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from feedback.event_detector import EventDetector

detector = EventDetector(
    purity_threshold=0.03,
    coherence_threshold=0.05,
    entropy_threshold=0.03,
)

rho_0 = np.array([
    [1.0, 0.0],
    [0.0, 0.0],
], dtype=complex)

rho_plus = 0.5 * np.array([
    [1.0, 1.0],
    [1.0, 1.0],
], dtype=complex)

rho_mixed = np.array([
    [0.5, 0.0],
    [0.0, 0.5],
], dtype=complex)

for rho in [rho_0, rho_plus, rho_mixed, rho_plus]:
    result = detector.detect(rho)
    print(result)