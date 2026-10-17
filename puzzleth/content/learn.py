"""Text for the Learn screen. Each topic is a list of pages; each page is a title and paragraphs.

A paragraph starting with "## " is drawn as a small heading.
"""

EXPECT = [
    ("Before the session", [
        "A cognitive assessment is a one-to-one session with a psychologist or a trained examiner. The core "
        "subtests usually take about an hour to an hour and a half, sometimes as part of a longer assessment.",
        "There is nothing to study and nothing to bring except glasses or hearing aids if you use them. Sleep, "
        "food and any medication you normally take matter more than any preparation.",
        "It is fine to be nervous. Examiners see nervous people every day, and the first few items on every "
        "subtest are easy on purpose, partly to help you settle in.",
        "You can ask questions before you start, and you can ask for a short break between subtests.",
    ]),
    ("What the examiner does", [
        "## They read from a script",
        "Instructions are read word for word, so that everyone gets exactly the same test. If they sound "
        "formal, that's why.",
        "## They won't tell you if you were right",
        "This is the part that unsettles people most. A neutral face or a plain \"okay\" after every answer is "
        "the rule for every examinee. It is not a sign that you got it wrong.",
        "## They time you and write things down",
        "A stopwatch is used openly on timed subtests, and spoken answers are written down word for word. "
        "That is normal procedure too.",
        "## They may ask \"Tell me more\"",
        "On the verbal subtests a vague answer is followed by a neutral prompt. It means the answer could earn "
        "more points if you explain further, not that it was wrong.",
    ]),
    ("Rules you might notice", [
        "## Starting partway in",
        "Adults usually begin a few items into a subtest, not at item 1. The examiner already knows where.",
        "## Going backwards",
        "If one of your first two answers isn't fully right, the examiner goes back to easier items. This is "
        "the reversal rule. It finds a solid starting point, and you then get credit for every easier item "
        "you skipped.",
        "## Stopping after a few misses",
        "Each subtest ends after a set number of wrong answers in a row (two to three, depending on the "
        "subtest). Everyone reaches that point, because the items keep getting harder until they are hard for "
        "almost everyone. Being stopped is the design, not a failure.",
        "## It's okay to say \"I don't know\"",
        "Guessing is allowed, and so is passing. You are not expected to answer everything.",
    ]),
    ("Afterwards", [
        "Your answers are compared with those of a large group of people your age, and turned into scores for "
        "each subtest, for each of the four areas, and overall.",
        "A good report gives ranges, not just single numbers, and puts the scores alongside your history, "
        "education and the reason you were tested. The numbers are one piece of a bigger picture.",
        "Uneven results are normal. Most people score noticeably higher in some areas than in others.",
        "If you practised with this game or anything like it, mention it to the examiner. Practice can raise "
        "scores a little, and they can take that into account.",
    ]),
]

SUBTESTS = [
    ("The ten subtests  (1 of 3)", [
        "## Block Design  ·  Perceptual Reasoning",
        "Copying a red-and-white pattern with blocks. Looks at breaking a picture into parts and building it "
        "again, under time pressure.",
        "## Similarities  ·  Verbal Comprehension",
        "\"How are a piano and a guitar alike?\" Looks at abstract verbal reasoning: finding the category, not "
        "a surface detail.",
        "## Digit Span  ·  Working Memory",
        "Repeating digits forwards, backwards and in order. Looks at holding information in mind and working "
        "with it.",
        "## Matrix Reasoning  ·  Perceptual Reasoning",
        "Finding the missing piece of a pattern. A classic test of fluid reasoning, which is solving new "
        "problems without relying on knowledge.",
    ]),
    ("The ten subtests  (2 of 3)", [
        "## Vocabulary  ·  Verbal Comprehension",
        "Explaining what words mean. Word knowledge is one of the best single predictors of the overall score.",
        "## Arithmetic  ·  Working Memory",
        "Word problems solved in your head. Less about maths skill than about holding the numbers in mind.",
        "## Symbol Search  ·  Processing Speed",
        "Spotting whether a symbol appears in a group, as fast as possible.",
    ]),
    ("The ten subtests  (3 of 3)", [
        "## Visual Puzzles  ·  Perceptual Reasoning",
        "Choosing the three pieces that make a shape. Looks at mental rotation and spatial reasoning.",
        "## Information  ·  Verbal Comprehension",
        "General-knowledge questions. Looks at knowledge picked up from school and everyday life.",
        "## Coding  ·  Processing Speed",
        "Copying symbols that match digits as fast as possible, using a key. Looks at speed and visual-motor "
        "coordination.",
    ]),
    ("Other versions", [
        "This game has ten core subtests in four areas. Real assessments can also have extra subtests that an "
        "examiner can add or swap in.",
        "Assessments are revised every so often: tasks are updated, the areas can be split up differently, and "
        "the scores are worked out again from new groups of people. Whichever version you meet, the session "
        "itself feels much the same.",
        "Children are assessed with a version made for their age, which works in a very similar way.",
    ]),
]

INDEXES = [
    ("The four areas", [
        "## Verbal Comprehension  (Similarities, Vocabulary, Information)",
        "Reasoning with words and the knowledge you have built up through language.",
        "## Perceptual Reasoning  (Block Design, Matrix Reasoning, Visual Puzzles)",
        "Reasoning with shapes and patterns: solving new visual problems without words.",
        "## Working Memory  (Digit Span, Arithmetic)",
        "Holding information in mind for a few seconds while doing something with it.",
        "## Processing Speed  (Symbol Search, Coding)",
        "How quickly and accurately you can do simple visual tasks.",
        "Each area is built from its subtests, and the overall result is built from all ten.",
    ]),
]

SCORES = [
    ("How scores work", [
        "## Compared with people your age",
        "Points on a subtest are compared with those of a large group of people your age. A score says where "
        "you stand among them, not how many answers you got right.",
        "## Subtests, areas and overall",
        "Each subtest gets a score, each of the four areas gets one from its subtests, and one overall result "
        "combines them all. About two in three people score close to the average on each of them.",
        "## Percentiles",
        "A percentile of 75 means you scored higher than 75 out of 100 people your age. It is not a percentage "
        "of answers correct.",
        "## Ranges, not points",
        "Any test has measurement error, so real reports give a confidence range instead of a single number. "
        "A small difference between two scores usually means nothing.",
    ]),
    ("Scores in this game", [
        "## Grade Scores",
        "The subtests, the four areas and the full assessment are graded from D up to S: D, C, B, A, and S for "
        "the very best. The full assessment's overall grade is your Grade Score. The standards behind the "
        "grades are made up for this game, so they only track your own progress. You can hide them in Settings.",
        "## Puzzle rating",
        "Rated sets work like a chess puzzle rating. Each puzzle has a difficulty level, and your rating rises "
        "when you solve one and falls when you miss one, by more when the result is a surprise. Puzzles are "
        "picked to match your rating, so you'll solve about half of them. The rating only compares you with "
        "the puzzles in this game.",
        "## Daily challenge",
        "Ten puzzles from one subtest, ramping from easy to beyond the real test's hardest item. Everyone gets "
        "the same puzzles each day. Only your first try of the day counts.",
    ]),
]

MYTHS = [
    ("Myths and facts", [
        "## \"Your score is fixed for life.\"",
        "Adult scores are fairly stable, but not set in stone. Education, health and life circumstances all "
        "play a part, and scores can change over years.",
        "## \"Brain training makes you smarter.\"",
        "Practice makes you better at the tasks you practise. Large reviews have found little evidence that "
        "the gains carry over to general intelligence. This game will make you better at these puzzles. It "
        "won't make you smarter.",
        "## \"An online test told me my real score.\"",
        "Real assessments are standardised on large, carefully chosen samples of people and given under "
        "controlled conditions. Online tests, including this game, are not, so their results can't be compared "
        "with real scores.",
    ]),
    ("Myths and facts  (continued)", [
        "## \"A test score measures your worth.\"",
        "These tests measure a specific set of reasoning, memory and speed skills. They say nothing about "
        "kindness, creativity, determination or most of what makes a life go well.",
        "## \"A big gap between my areas means something is wrong.\"",
        "Clear gaps between areas are common in the general population. Only a qualified professional, looking "
        "at the whole picture, can say whether a pattern matters.",
        "## \"Scores keep going up over generations.\"",
        "Partly true. Average scores rose steadily during the 20th century (the Flynn effect). That's one "
        "reason tests are re-normed every so often.",
    ]),
]

ABOUT = [
    ("About Puzzleth", [
        "Puzzleth is a training game modelled on the structure and administration rules of real one-to-one "
        "cognitive assessments. Every puzzle is generated by the game. No real test's items are used, and the "
        "game is not affiliated with or endorsed by any test publisher.",
        "## This is not a psychological test",
        "Its grades come from rough standards made up for this game. They can't be compared with the results "
        "of a real assessment, can't diagnose anything, and must not be used for school, work, legal or medical "
        "decisions.",
        "## Who it's for",
        "People who are nervous about an upcoming assessment and want to know what it's like. People who love "
        "a hard puzzle. And anyone curious about how these assessments work.",
    ]),
]

TOPICS = [
    ("expect", "What to expect", EXPECT),
    ("subtests", "The ten subtests", SUBTESTS),
    ("indexes", "The four areas", INDEXES),
    ("scores", "How scores work", SCORES),
    ("myths", "Myths and facts", MYTHS),
    ("about", "About this game", ABOUT),
]


def topics(language):
    """TOPICS in ``language``: from learn_<language> for the translations, which keep the same keys."""
    from . import learn_fr, learn_ro
    return {"ro": learn_ro.TOPICS, "fr": learn_fr.TOPICS}.get(language, TOPICS)
