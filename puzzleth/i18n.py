"""The game's languages, and translation of its text.

English text in the code is the key into each language's catalog (``puzzleth/locales``). Text drawn
with gfx is translated as it is drawn, so fixed labels need nothing more. Text with numbers or names
in it goes through ``f`` (or ``n`` when a count decides the wording), which translates the template
before filling it in.

A language has, besides its catalog: its own verbal items (content/verbal_<code>.py), its Learn
pages (content/learn_<code>.py) and its spoken digits (sounds/<code>/, from tools/make_sounds.py).
The tests check that each of them is complete.
"""

from .locales import fr, ro

LANGUAGES = (
    ("en", "English"),
    ("ro", "Română"),
    ("fr", "Français"),
)

_CATALOGS = {"en": {}, "ro": ro.STRINGS, "fr": fr.STRINGS}
_ABBREVIATIONS = {"en": {}, "ro": ro.ABBREVIATIONS, "fr": fr.ABBREVIATIONS}

_language = "en"


def set_language(language):
    global _language
    _language = language if language in _CATALOGS else "en"


def language():
    return _language


def translate(text, language):
    """``text`` in ``language``, or unchanged if it isn't in that language's catalog."""
    text = str(text)
    return _CATALOGS.get(language, {}).get(text, text)


def _(text):
    return translate(text, _language)


def f(template, **values):
    """Translate ``template``, then fill in its ``{name}`` fields."""
    return _(template).format(**values)


def de(count):
    """Romanian puts "de" between a number and its noun from 20 on: "3 mere", "20 de mere"."""
    rest = abs(count) % 100
    return "de " if rest >= 20 or (rest == 0 and count != 0) else ""


def n(count, one, other, **values):
    """The singular or plural template for ``count`` (also given as ``{n}``), translated and filled in.

    Romanian templates can also use ``{de}`` before the noun."""
    forms = _CATALOGS.get(_language, {}).get((one, other), (one, other))
    single = count in (0, 1) if _language == "fr" else count == 1
    return (forms[0] if single else forms[1]).format(n=count, de=de(count), **values)


def abbr(code):
    """A subtest or index abbreviation (BD, VCI, FSIQ...) as tests in this language write it."""
    return _ABBREVIATIONS.get(_language, {}).get(code, code)


def upper(text):
    """Translated, then in capitals."""
    return _(text).upper()


def decimal(x, places=1):
    """``x`` with ``places`` decimals: "4.5" in English, "4,5" in Romanian and French."""
    s = f"{x:.{places}f}"
    return s if _language == "en" else s.replace(".", ",")
