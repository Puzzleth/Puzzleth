#!/usr/bin/env python3
"""Regenerate the bundled sounds in puzzleth/sounds/.

Sound effects are synthesized here from sine waves. The spoken digits come from Piper
(https://github.com/rhasspy/piper): English with its LJSpeech voice, whose training data is public
domain, Romanian with its Mihai voice (CC0 data) and French with its SIWIS voice (CC BY 4.0 data).
Needs ffmpeg, and for the digits also the piper command and the voice model:

    tools/make_sounds.py --voice path/to/en_US-ljspeech-high.onnx
    tools/make_sounds.py --language ro --voice path/to/ro_RO-mihai-medium.onnx
    tools/make_sounds.py --language fr --voice path/to/fr_FR-siwis-medium.onnx
    tools/make_sounds.py                       # effects only, keeps the existing digits

The voice models are at huggingface.co/rhasspy/piper-voices (en/en_US/ljspeech/high,
ro/ro_RO/mihai/medium, fr/fr_FR/siwis/medium). English digits go in puzzleth/sounds/, the others in
puzzleth/sounds/<language>/, where they replace the English ones while that language is chosen.
To use your own sound instead, see puzzleth/sounds/README.md.
"""
import argparse
import array
import math
import os
import random
import subprocess
import tempfile
import wave

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "puzzleth", "sounds")
RATE = 44100
DIGITS = {
    "en": ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"],
    "ro": ["unu", "doi", "trei", "patru", "cinci", "șase", "șapte", "opt", "nouă"],
    "fr": ["un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"],
}


def silence(dur):
    return [0.0] * int(RATE * dur)


def tone(freq, dur, amp=0.5, decay=8.0, attack=0.004, partials=((1, 1.0),), glide=0.0):
    """A plucked or bell-like note: a few sine partials under an exponential decay."""
    out = []
    phase = [0.0] * len(partials)
    for i in range(int(RATE * dur)):
        t = i / RATE
        f = freq * (1 + glide * t / dur)
        env = min(1.0, t / attack) * math.exp(-decay * t)
        s = 0.0
        for k, (mult, gain) in enumerate(partials):
            phase[k] += 2 * math.pi * f * mult / RATE
            s += gain * math.sin(phase[k])
        out.append(amp * env * s)
    return out


def mix(*parts):
    """Overlay (offset_seconds, samples) pairs."""
    n = max(int(RATE * off) + len(s) for off, s in parts)
    out = [0.0] * n
    for off, s in parts:
        o = int(RATE * off)
        for i, v in enumerate(s):
            out[o + i] += v
    return out


BELL = ((1, 1.0), (2, 0.35), (3, 0.12), (4.2, 0.05))
SOFT = ((1, 1.0), (2, 0.15))


def effects():
    rnd = random.Random(1)
    noise = [rnd.uniform(-1, 1) * math.exp(-i / (RATE * 0.004)) * 0.15 for i in range(int(RATE * 0.02))]
    return {
        # buttons and on-screen keys
        "tap": mix((0, tone(1500, 0.05, 0.22, decay=90, partials=SOFT)), (0, noise)),
        # typing a digit
        "key": tone(1100, 0.04, 0.16, decay=110, partials=SOFT),
        # choosing or un-choosing a piece, turning a block
        "select": mix((0, tone(880, 0.07, 0.2, decay=50, partials=SOFT)),
                      (0.035, tone(1320, 0.08, 0.16, decay=50, partials=SOFT))),
        # an answer was given, with no hint of whether it was right (test conditions)
        "submit": tone(520, 0.18, 0.3, decay=22, partials=SOFT),
        # one answer during the timed part of Symbol Search and Coding
        "blip": tone(980, 0.06, 0.18, decay=70, partials=SOFT),
        "correct": mix((0, tone(1046.5, 0.5, 0.26, decay=7, partials=BELL)),
                       (0.09, tone(1568.0, 0.6, 0.24, decay=6, partials=BELL))),
        "partial": tone(784.0, 0.45, 0.3, decay=8, partials=BELL),
        "wrong": mix((0, tone(392.0, 0.3, 0.28, decay=10, partials=SOFT)),
                     (0.13, tone(311.1, 0.4, 0.28, decay=8, partials=SOFT))),
        # last seconds of a time limit
        "tick": tone(1900, 0.03, 0.18, decay=160, partials=((1, 1.0), (2.7, 0.3))),
        "timeup": mix((0, tone(440.0, 0.6, 0.26, decay=5, partials=BELL)),
                      (0.0, tone(554.4, 0.6, 0.16, decay=5, partials=BELL))),
        # a subtest, set or the full assessment is finished
        "complete": mix(*[(i * 0.11, tone(f, 1.1 - i * 0.11, 0.2, decay=4.5, partials=BELL))
                          for i, f in enumerate((523.3, 659.3, 784.0, 1046.5))]),
    }


def write_wav(path, samples, rate=RATE):
    peak = max(1e-9, max(abs(s) for s in samples))
    k = 0.95 / peak if peak > 0.95 else 1.0
    data = array.array("h", (int(max(-1, min(1, s * k)) * 32767) for s in samples))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(data.tobytes())


def read_wav(path):
    with wave.open(path, "rb") as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2
        rate = w.getframerate()
        data = array.array("h", w.readframes(w.getnframes()))
    return [v / 32768 for v in data], rate


def to_ogg(wav, name, out=OUT):
    dst = os.path.join(out, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "4", dst],
                   check=True)
    return dst


def speak(model, word, tmp, length_scale):
    raw = os.path.join(tmp, word + "_raw.wav")
    subprocess.run(["piper", "-m", model, "-f", raw, "--length-scale", str(length_scale)],
                   input=word.capitalize() + ".", text=True, check=True, capture_output=True)
    s, rate = read_wav(raw)
    # trim the silence around the word, then fade the edges so it doesn't click
    thresh = 0.02 * max(abs(v) for v in s)
    first = next(i for i, v in enumerate(s) if abs(v) > thresh)
    last = len(s) - next(i for i, v in enumerate(reversed(s)) if abs(v) > thresh)
    s = s[max(0, first - int(rate * 0.01)):last + int(rate * 0.04)]
    fade = int(rate * 0.008)
    for i in range(fade):
        s[i] *= i / fade
        s[-1 - i] *= i / fade
    peak = max(abs(v) for v in s)
    s = [v * 0.9 / peak for v in s]
    return s, rate


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--voice", help="Piper .onnx voice model; regenerates the spoken digits")
    ap.add_argument("--language", choices=sorted(DIGITS), default="en", help="language of the spoken digits")
    ap.add_argument("--length-scale", type=float, default=0.9, help="Piper speaking speed (smaller is faster)")
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    digits_out = OUT if args.language == "en" else os.path.join(OUT, args.language)
    os.makedirs(digits_out, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        if args.language == "en":   # the effects are the same in every language
            for name, samples in effects().items():
                wav = os.path.join(tmp, name + ".wav")
                write_wav(wav, samples)
                print(to_ogg(wav, name))
        if args.voice:
            for d, word in enumerate(DIGITS[args.language], 1):
                s, rate = speak(args.voice, word, tmp, args.length_scale)
                if len(s) / rate > 0.7:   # each digit must fit in its one-second slot
                    print(f"warning: '{word}' lasts {len(s) / rate:.2f} s")
                wav = os.path.join(tmp, f"digit{d}.wav")
                write_wav(wav, s, rate)
                print(to_ogg(wav, f"digit{d}", digits_out), f"{len(s) / rate:.2f} s")


if __name__ == "__main__":
    main()
