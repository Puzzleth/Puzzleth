"""Raw score -> scaled score -> index score -> FSIQ, following the WAIS-IV structure.

The real WAIS norms are proprietary and depend on the exact items, so these are rough
approximations tuned to this game's versions of the subtests (e.g. multiple-choice verbal
items are easier than free recall). Treat every number as a training estimate, not a real IQ.
"""
import math

# code -> (approximate adult mean raw score, standard deviation)
NORMS = {
    "BD": (44, 11),
    "SI": (26, 5),
    "DS": (27, 5),
    "MR": (17, 4.5),
    "VC": (42, 9),
    "AR": (14, 3.5),
    "SS": (33, 7),
    "VP": (15, 4.5),
    "IN": (16, 4.5),
    "CD": (80, 16),
}

INDEX_SUBTESTS = {
    "VCI": ["SI", "VC", "IN"],
    "PRI": ["BD", "MR", "VP"],
    "WMI": ["DS", "AR"],
    "PSI": ["SS", "CD"],
}

# Typical inter-subtest correlations used to turn a mean of scaled scores into a composite.
_R_INDEX = 0.6
_R_FSIQ = 0.45


def scaled_score(code, raw):
    mean, sd = NORMS[code]
    return int(max(1, min(19, round(10 + 3 * (raw - mean) / sd))))


def _composite(scaled, r, lo, hi):
    n = len(scaled)
    z = (sum(scaled) / n - 10) / 3
    z /= math.sqrt((1 + (n - 1) * r) / n)
    return int(max(lo, min(hi, round(100 + 15 * z))))


def index_score(scaled):
    return _composite(scaled, _R_INDEX, 50, 150)


def fsiq(scaled):
    return _composite(scaled, _R_FSIQ, 40, 160)


def compute_indexes(scaled_by_code):
    """Returns ({index: score}, fsiq or None) using whatever subtests are available."""
    out = {}
    for idx, codes in INDEX_SUBTESTS.items():
        if all(c in scaled_by_code for c in codes):
            out[idx] = index_score([scaled_by_code[c] for c in codes])
    all_codes = [c for codes in INDEX_SUBTESTS.values() for c in codes]
    full = fsiq([scaled_by_code[c] for c in all_codes]) if all(c in scaled_by_code for c in all_codes) else None
    return out, full


def percentile(score, mean=100, sd=15):
    z = (score - mean) / sd
    p = 50 * (1 + math.erf(z / math.sqrt(2)))
    return max(0.1, min(99.9, p))


def scaled_percentile(scaled):
    return percentile(scaled, 10, 3)


def classification(score):
    """WAIS-IV qualitative descriptors for composite scores."""
    if score >= 130:
        return "Very Superior"
    if score >= 120:
        return "Superior"
    if score >= 110:
        return "High Average"
    if score >= 90:
        return "Average"
    if score >= 80:
        return "Low Average"
    if score >= 70:
        return "Borderline"
    return "Extremely Low"


def scaled_label(s):
    if s >= 16:
        return "Very High"
    if s >= 13:
        return "Above Average"
    if s >= 8:
        return "Average"
    if s >= 5:
        return "Below Average"
    return "Low"
