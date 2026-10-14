"""Text for the Learn screen. Each topic is a list of pages; each page is a title and paragraphs.

A paragraph starting with "## " is drawn as a small heading.
"""

EXPECT = [
    ("Before the session", [
        "A WAIS assessment is a one-to-one session with a psychologist or a trained examiner. The ten core "
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
        "Your answers are turned into scaled scores for each subtest (1 to 19, average 10), then four index "
        "scores and a Full Scale IQ (average 100).",
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
    ("Editions", [
        "This game follows the WAIS-IV (2008): ten core subtests making four index scores. The real WAIS-IV also "
        "has five supplementary subtests that an examiner can add or swap in.",
        "A newer edition, the WAIS-5, was published in 2024. It splits Perceptual Reasoning into Visual Spatial "
        "and Fluid Reasoning, and builds the Full Scale IQ from fewer subtests. Many clinics still use the "
        "WAIS-IV, and the session itself feels much the same.",
        "Children are tested with a different test, the WISC, which works in a very similar way.",
    ]),
]

INDEXES = [
    ("The four index scores", [
        "## Verbal Comprehension  (Similarities, Vocabulary, Information)",
        "Reasoning with words and the knowledge you have built up through language.",
        "## Perceptual Reasoning  (Block Design, Matrix Reasoning, Visual Puzzles)",
        "Reasoning with shapes and patterns: solving new visual problems without words.",
        "## Working Memory  (Digit Span, Arithmetic)",
        "Holding information in mind for a few seconds while doing something with it.",
        "## Processing Speed  (Symbol Search, Coding)",
        "How quickly and accurately you can do simple visual tasks.",
        "Each index is built from its subtests, and the Full Scale IQ is built from all ten.",
    ]),
]

SCORES = [
    ("How scores work", [
        "## Raw score to scaled score",
        "Points on a subtest are compared with people of your age and turned into a scaled score from 1 to 19. "
        "10 is average, and about two in three people score between 7 and 13.",
        "## Index scores and Full Scale IQ",
        "These use a different scale: 100 is average, and every 15 points is one standard deviation. About two "
        "in three people score between 85 and 115, and about 2 in 100 score above 130.",
        "## Percentiles",
        "A percentile of 75 means you scored higher than 75 out of 100 people your age. It is not a percentage "
        "of answers correct.",
        "## Ranges, not points",
        "Any test has measurement error, so real reports give a confidence range, such as 102 to 112. A few "
        "points of difference between two scores usually mean nothing.",
    ]),
    ("Scores in this game", [
        "## Test-style scores",
        "The full assessment and the WAIS-style subtests show scaled scores, index scores and a Full Scale "
        "Score (the game's stand-in for a Full Scale IQ), so you can see how a real score report is put together. The norms behind them are made up for this "
        "game, so the numbers only track your own progress. You can hide them in Settings.",
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
        "## \"IQ is fixed for life.\"",
        "Adult scores are fairly stable, but not set in stone. Education, health and life circumstances all "
        "play a part, and scores can change over years.",
        "## \"Brain training raises your IQ.\"",
        "Practice makes you better at the tasks you practise. Large reviews have found little evidence that "
        "the gains carry over to general intelligence. This game will make you better at these puzzles. It "
        "won't make you smarter.",
        "## \"An online IQ test told me my IQ.\"",
        "Real IQ tests are standardised on large, carefully chosen samples of people and given under controlled "
        "conditions. Online tests, including this game, are not, so their numbers can't be compared with real "
        "scores.",
    ]),
    ("Myths and facts  (continued)", [
        "## \"IQ measures your worth.\"",
        "IQ tests measure a specific set of reasoning, memory and speed skills. They say nothing about kindness, "
        "creativity, determination or most of what makes a life go well.",
        "## \"A big gap between my index scores means something is wrong.\"",
        "Gaps of 10 or more points between index scores are common in the general population. Only a qualified "
        "professional, looking at the whole picture, can say whether a pattern matters.",
        "## \"Scores keep going up over generations.\"",
        "Partly true. Average scores rose by about 3 points per decade during the 20th century (the Flynn "
        "effect). That's one reason tests are re-normed every so often.",
    ]),
]

ABOUT = [
    ("About Puzzleth", [
        "Puzzleth is a free, open-source training game modelled on the structure and administration rules "
        "of the WAIS-IV. Every puzzle is generated by the game. None of the real test's items are used, and the "
        "game is not affiliated with or endorsed by the test's publisher.",
        "## This is not an actual IQ test",
        "Its scores come from approximate norms made up for this game. They can't be compared with a real IQ, "
        "can't diagnose anything, and must not be used for school, work, legal or medical decisions.",
        "## Who it's for",
        "People who are nervous about an upcoming assessment and want to know what it's like. People who love "
        "a hard puzzle. And anyone curious about how intelligence tests work.",
    ]),
]

TOPICS = [
    ("expect", "What to expect", EXPECT),
    ("subtests", "The ten subtests", SUBTESTS),
    ("indexes", "The four indexes", INDEXES),
    ("scores", "How scores work", SCORES),
    ("myths", "IQ myths and facts", MYTHS),
    ("about", "About this game", ABOUT),
]
