"""Raw score -> skill points -> area and overall points -> Grade Scores (D, C, B, A, S).

The norms are rough standards made up for this game's versions of the subtests (e.g. multiple-choice
verbal items are easier than free recall). Players only ever see letter grades; the points behind
them are an internal step. Treat every grade as a training estimate, nothing more.
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

# Typical inter-subtest correlations used to turn a mean of skill points into an area or overall value.
_R_INDEX = 0.6
_R_OVERALL = 0.45

# Grades from the lowest to the best of the best, and how far above the average (in standard
# deviations) each one starts: B is around average, S is the top two or three in a hundred.
GRADES = ("D", "C", "B", "A", "S")
_GRADE_FROM = {"S": 2.0, "A": 1.0, "B": -1 / 3, "C": -4 / 3}
GRADE_NAMES = {
    "S": "Outstanding",
    "A": "Excellent",
    "B": "Solid",
    "C": "Developing",
    "D": "Just getting started",
}


def scaled_score(code, raw):
    """Skill points, 1 to 19 (10 is average): one per pip on the subtest's ring."""
    mean, sd = NORMS[code]
    return int(max(1, min(19, round(10 + 3 * (raw - mean) / sd))))


def _composite(scaled, r, lo, hi):
    n = len(scaled)
    z = (sum(scaled) / n - 10) / 3
    z /= math.sqrt((1 + (n - 1) * r) / n)
    return int(max(lo, min(hi, round(100 + 15 * z))))


def index_score(scaled):
    return _composite(scaled, _R_INDEX, 50, 150)


def overall_score(scaled):
    return _composite(scaled, _R_OVERALL, 40, 160)


def compute_indexes(scaled_by_code):
    """Returns ({area: points}, overall points or None) using whatever subtests are available."""
    out = {}
    for idx, codes in INDEX_SUBTESTS.items():
        if all(c in scaled_by_code for c in codes):
            out[idx] = index_score([scaled_by_code[c] for c in codes])
    all_codes = [c for codes in INDEX_SUBTESTS.values() for c in codes]
    full = overall_score([scaled_by_code[c] for c in all_codes]) if all(c in scaled_by_code for c in all_codes) else None
    return out, full


def _grade(z):
    for letter in ("S", "A", "B", "C"):
        if z >= _GRADE_FROM[letter] - 1e-9:
            return letter
    return "D"


def grade(scaled):
    """A subtest's grade from its skill points."""
    return _grade((scaled - 10) / 3)


def composite_grade(score):
    """An area's or the overall Grade Score from its points."""
    return _grade((score - 100) / 15)


def grade_rank(letter):
    """0 for D up to 4 for S."""
    return GRADES.index(letter)


def grade_name(letter):
    return GRADE_NAMES[letter]
