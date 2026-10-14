# Brain Puzzlerer

A WAIS-style cognitive training game. It recreates the structure and administration rules of
the ten core WAIS-IV subtests with procedurally generated items, so every run is new. Your
results are shown as a skill-point constellation.

> **Not a real IQ test.** The real WAIS norms are proprietary and depend on the exact items, so
> scores here use approximate norms tuned to this game. Use them to track your own progress.

## Running

```sh
./puzzle

# or manually, on NixOS / nix
nix-shell --run "python3 main.py"

# anywhere else (Python 3.10+)
pip install -r requirements.txt
python3 main.py
```

Progress is saved to `~/.brain_puzzlerer/profile.json`.

## How it works

**Skill tree.** The menu is a constellation. Each subtest node is a ring of **19 skill points**,
one per scaled-score point (the WAIS scale runs 1–19 with mean 10, SD 3). Dim points show your
personal best. Index nodes (VCI, PRI, WMI, PSI) and the central **Full Scale IQ** node are
progress rings over their score ranges, with a tick marking the population mean of 100.
Click any subtest node to train it on its own.

**Full assessment.** Runs all ten subtests in the real WAIS-IV order under test conditions (no
feedback), then animates your constellation and shows the index scores and FSIQ.

**Feedback mode** (training only). After each item it shows how the item was scored, e.g.
why "Both are fruits" earns 2 points but "Both can be eaten" earns 1.

| Index | Subtest | Notes |
|---|---|---|
| Verbal Comprehension | Similarities, Vocabulary, Information | Multiple choice, with options written to match WAIS 2/1/0 scoring |
| Perceptual Reasoning | Block Design, Matrix Reasoning, Visual Puzzles | Fully procedural; every puzzle is checked to have exactly one solution |
| Working Memory | Digit Span (forward/backward/sequencing), Arithmetic | 1 digit/sec; Arithmetic hides the problem after it is "read" |
| Processing Speed | Symbol Search, Coding | 120-second limits; Coding uses symbol→digit lookup |

WAIS administration rules are implemented: adult **start points**, **reversal** (earlier items in
reverse order until two consecutive perfect scores, with full credit below), **discontinue**
rules, per-item **time limits**, and Block Design **speed bonuses**.

## Scoring

`raw → scaled = 10 + 3·(raw − mean)/SD` (clamped to 1–19). A composite turns the mean of z-scores
into an index score, accounting for inter-subtest correlation:
`z = mean_z / sqrt((1 + (n−1)·r) / n)` and `index = 100 + 15·z`.

## Tests

```sh
nix-shell --run "python3 -m unittest discover -s tests"
```

The tests cover the administration rules, the scoring math, and the generators. For the
generators, they check thousands of random seeds for a unique matrix answer, exactly one
Visual Puzzles solution, integer arithmetic answers, and valid Symbol Search rows.
