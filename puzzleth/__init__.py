"""Puzzleth: a cognitive puzzle training game."""

VERSION = "0.0.4"
STAGE = "NIGHTLY"


def version_label():
    """How the version is shown in the game, e.g. "v0.0.3 PRE-ALPHA"."""
    return f"v{VERSION} {STAGE}" if STAGE else f"v{VERSION}"
