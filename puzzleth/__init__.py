"""Puzzleth: a WAIS-style puzzle game."""

VERSION = "0.0.1"
STAGE = "PRE-ALPHA"


def version_label():
    """How the version is shown in the game, e.g. "v0.0.1 (PRE-ALPHA)"."""
    return f"v{VERSION} ({STAGE})" if STAGE else f"v{VERSION}"
