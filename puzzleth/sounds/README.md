# Sounds

Every sound in Puzzleth is one of these files. To change one, add your own file with the same
name, as `.wav`, `.mp3` or `.ogg`:

- **Here**, in `puzzleth/sounds/`. A `.wav` or `.mp3` is used instead of the `.ogg` already here,
  and it goes into the web version too.
- **Or in `~/.puzzleth/sounds/`** (desktop only), which leaves the game's own files alone.

To silence one sound, use a file with no sound in it. Restart the game to hear changes.

| File | When it plays |
|---|---|
| `digit1` … `digit9` | Digit Span reads each digit out as it appears (one per second, so keep them under 0.7 s). The Romanian and French ones are in `ro/` and `fr/`, used while that language is chosen (`~/.puzzleth/sounds/ro/` and `fr/` override them) |
| `tap` | Any button or on-screen key |
| `key` | Typing a digit, deleting one, turning a Block Design block |
| `select` | Choosing or un-choosing a Visual Puzzles piece |
| `correct` | A right answer, when feedback is shown (training, samples, rated sets, daily challenge) |
| `partial` | Partial credit, when feedback is shown |
| `wrong` | A wrong answer, when feedback is shown |
| `submit` | An answer under test conditions, where you aren't told if it was right |
| `blip` | Each answer in the timed part of Symbol Search and Coding |
| `tick` | Each of the last 5 seconds of a time limit |
| `timeup` | A time limit runs out |
| `complete` | A subtest, puzzle set or the full assessment is finished |

How loud each one plays, compared with the others, is set in `LEVELS` in `puzzleth/sound.py`. The
Sound effects setting turns them all up or down.

`tools/make_sounds.py` makes the original files: it synthesizes the effects and has
[Piper](https://github.com/rhasspy/piper) speak the digits: in English with its LJSpeech voice,
whose recordings are public domain; in Romanian with its Mihai voice, trained on recordings
released under CC0; and in French with its SIWIS voice, trained on the
[SIWIS French Speech Synthesis Database](https://datashare.is.ed.ac.uk/handle/10283/2353)
(Junichi Yamagishi, Pierre-Edouard Honnet, Philip Garner and Alexandros Lazaridis, CC BY 4.0).

## Music

Put your own music files (`.mp3`, `.ogg` or `.wav`) in `puzzleth/music/`, or on the desktop in
`~/.puzzleth/music/`. Puzzleth plays all of them in a shuffled loop, fading each one in at the
start and out at the end (`FADE_IN` and `FADE_OUT` in `puzzleth/sound.py`, in seconds). The Music
setting sets the volume. The music turns down while Digit Span reads digits out. In a browser it
starts at your first click, tap or key press, since browsers don't allow sound before that.
