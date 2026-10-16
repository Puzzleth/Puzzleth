"""French. The player is addressed with "vous"; subtest and index names are those of the French WAIS-IV."""
import re

ABBREVIATIONS = {
    "BD": "CUB", "SI": "SIM", "DS": "MCH", "MR": "MAT", "VC": "VOC",
    "AR": "ARI", "SS": "SYM", "VP": "PUZ", "IN": "INF", "CD": "COD",
    "VCI": "ICV", "PRI": "IRP", "WMI": "IMT", "PSI": "IVT",
}

NBSP = " "


def spacing(s):
    """French typography: a non-breaking space before ? ! : ; and inside « », and between the
    groups of a number like 300 000, so that none of them can be wrapped onto a line of its own."""
    s = re.sub(r" ([?!:;»])", NBSP + r"\1", s)
    s = re.sub(r"« ", "«" + NBSP, s)
    return re.sub(r"(\d) (\d{3})\b", r"\1" + NBSP + r"\2", s)


STRINGS = {
    # ---------------------------------------------------------------- language choice, disclaimer
    "Choose your language": "Choisissez votre langue",
    "The game will use this language. You can change it later in Settings.":
        "Le jeu utilisera cette langue. Vous pourrez la changer plus tard dans les paramètres.",
    "You can change it again any time in Settings.": "Vous pourrez la changer à tout moment dans les paramètres.",
    "Language": "Langue",
    "I understand": "J'ai compris",
    "This is not an actual IQ test": "Ceci n'est pas un vrai test de QI",
    "Puzzleth is a training game modelled on the structure and rules of the WAIS-IV. It is not the WAIS, uses "
    "none of its items, and is not affiliated with or endorsed by its publisher.":
        "Puzzleth est un jeu d'entraînement inspiré de la structure et des règles de la WAIS-IV. Ce n'est pas la "
        "WAIS : il n'en utilise aucun item et n'est ni affilié à son éditeur, ni approuvé par lui.",
    "Scores come from approximate norms made up for this game, not from a standardised sample of people. The "
    "scores shown here cannot be compared with a real IQ score.":
        "Les scores reposent sur des normes approximatives inventées pour ce jeu, pas sur un échantillon "
        "étalonné. Ils ne sont pas comparables à un vrai score de QI.",
    "It cannot diagnose anything and must not be used for school, work, legal or medical decisions. Only a "
    "standardised test given by a qualified psychologist produces a real IQ.":
        "Il ne permet aucun diagnostic et ne doit pas servir à des décisions scolaires, professionnelles, "
        "juridiques ou médicales. Seul un test étalonné, fait par un psychologue qualifié, donne un vrai QI.",
    "Practising test formats can raise scores on a real test. If you take a clinical assessment, tell the "
    "examiner you have practised.":
        "S'entraîner aux formats de test peut améliorer les scores à un vrai test. Si vous passez un bilan "
        "clinique, dites à l'examinateur que vous vous êtes entraîné.",

    # ---------------------------------------------------------------- menu
    "Begin Full Assessment": "Évaluation complète",
    "Daily": "Défi",
    "Daily  {solved}/10": "Défi  {solved}/10",
    "Learn": "Apprendre",
    "Leaderboard": "Classement",
    "Settings": "Paramètres",
    "About": "À propos",
    "Quit": "Quitter",
    "Support Development": "Soutenir le projet",
    "Update available": "Mise à jour disponible",
    "WAIS-style cognitive training": "Entraînement cognitif façon WAIS",
    "{n} / 10 skills measured  ·  click any node to train it":
        "{n} / 10 compétences  ·  cliquez-en une pour l'entraîner",
    "{n} / 10 skills measured  ·  tap any node to train it":
        "{n}/10 compétences  ·  touchez-en une pour l'entraîner",
    "  ·  daily streak {streak}": "  ·  série quotidienne : {streak}",
    "Not an actual IQ test. Scores are training estimates, not clinical results.":
        "Pas un vrai test de QI. Les scores sont des estimations, pas des résultats cliniques.",
    "Turn your phone sideways": "Tournez votre téléphone",
    "Puzzleth is played in landscape": "Puzzleth se joue en mode paysage",

    # ---------------------------------------------------------------- skill tree and its tooltips
    "SCORE": "SCORE",
    "scores hidden": "scores masqués",
    "FULL SCALE SCORE": "SCORE GLOBAL",
    "complete all 10": "faites les 10",
    ("{n} attempt", "{n} attempts"): ("{n} tentative", "{n} tentatives"),
    "Measured  ·  scores hidden  ·  {attempts}": "Mesuré  ·  scores masqués  ·  {attempts}",
    "Measured  ·  scores hidden": "Mesuré  ·  scores masqués",
    "Scaled score {score} / 19  ·  {label}": "Note standard {score} / 19  ·  {label}",
    "Percentile ≈ {percentile}": "Centile ≈ {percentile}",
    "  ·  raw {raw} / {max}": "  ·  note brute {raw} / {max}",
    "Not yet measured": "Pas encore mesuré",
    "Personal best {score}  ·  {attempts}": "Record personnel {score}  ·  {attempts}",
    "Puzzle rating {rating}  ·  peak {peak}": "Cote puzzles {rating}  ·  record {peak}",
    "Rated puzzle sets available": "Séries classées disponibles",
    "Index score {score}  ·  {label}": "Indice {score}  ·  {label}",
    "Complete all of its subtests to compute it": "Terminez toutes ses épreuves pour le calculer",
    "Combines all ten core subtests": "Combine les dix épreuves principales",
    "Training estimate, not a real IQ": "Estimation d'entraînement, pas un vrai QI",
    "Take the full assessment to compute it": "Passez l'évaluation complète pour le calculer",
    "Full Scale Score": "Score global",

    # ---------------------------------------------------------------- subtests, indexes, classifications
    "Block Design": "Cubes",
    "Similarities": "Similitudes",
    "Digit Span": "Mémoire des chiffres",
    "Matrix Reasoning": "Matrices",
    "Vocabulary": "Vocabulaire",
    "Arithmetic": "Arithmétique",
    "Symbol Search": "Symboles",
    "Visual Puzzles": "Puzzles visuels",
    "Information": "Information",
    "Coding": "Code",
    "Verbal Comprehension": "Compréhension verbale",
    "Perceptual Reasoning": "Raisonnement perceptif",
    "Working Memory": "Mémoire de travail",
    "Processing Speed": "Vitesse de traitement",
    "Very Superior": "Très supérieur",
    "Superior": "Supérieur",
    "High Average": "Moyen fort",
    "Average": "Moyen",
    "Low Average": "Moyen faible",
    "Borderline": "Limite",
    "Extremely Low": "Très faible",
    "Very High": "Très élevé",
    "Above Average": "Au-dessus de la moyenne",
    "Below Average": "Au-dessous de la moyenne",
    "Low": "Faible",

    # ---------------------------------------------------------------- what each subtest measures
    "Visual-spatial analysis and construction": "Analyse et construction visuospatiales",
    "Verbal concept formation and abstract reasoning": "Formation de concepts verbaux et raisonnement abstrait",
    "Auditory working memory, attention and mental manipulation":
        "Mémoire de travail auditive, attention et manipulation mentale",
    "Fluid reasoning and abstract pattern detection": "Raisonnement fluide et détection de régularités abstraites",
    "Word knowledge and verbal concept formation": "Connaissance des mots et formation de concepts verbaux",
    "Mental manipulation, concentration and numerical reasoning":
        "Manipulation mentale, concentration et raisonnement numérique",
    "Visual scanning speed and discrimination": "Vitesse d'exploration visuelle et discrimination",
    "Spatial reasoning and mental rotation": "Raisonnement spatial et rotation mentale",
    "General knowledge acquired from culture and education":
        "Connaissances générales acquises par la culture et l'éducation",
    "Processing speed, visual-motor coordination and associative learning":
        "Vitesse de traitement, coordination visuo-motrice et apprentissage associatif",

    # ---------------------------------------------------------------- rules of the real test
    "Recreate the model design using blocks with red, white and half-red/half-white faces.":
        "Reproduire le modèle avec des cubes aux faces rouges, blanches et mi-rouges mi-blanches.",
    "Items 1–8 use 4 blocks (2×2); items 9–14 use 9 blocks (3×3).":
        "Les items 1–8 utilisent 4 cubes (2×2) ; les items 9–14 en utilisent 9 (3×3).",
    "Time limits: 30 s (items 1–4), 60 s (5–8), 120 s (9–14).":
        "Temps limites : 30 s (items 1–4), 60 s (5–8), 120 s (9–14).",
    "Items 1–2: 2 pts. Items 3–8: 4 pts. Items 9–14: 4 pts plus up to 3 speed-bonus points.":
        "Items 1–2 : 2 pts. Items 3–8 : 4 pts. Items 9–14 : 4 pts plus jusqu'à 3 points de bonus de rapidité.",
    "Later models have no guide lines — you must work out where each block's edges are.":
        "Les derniers modèles n'ont plus de lignes de repère — à vous de trouver les bords des cubes.",
    "Adults start at item 5; reversal rule applies. Discontinue after 2 consecutive scores of 0.":
        "Les adultes commencent à l'item 5 ; règle du retour en arrière. Arrêt après 2 notes de 0 consécutives.",
    "Two words are read aloud; you explain how they are alike.":
        "Deux mots sont lus à voix haute ; vous expliquez en quoi ils se ressemblent.",
    "2 points: the abstract, general category the two belong to.":
        "2 points : la catégorie générale et abstraite commune aux deux.",
    "1 point: a concrete, specific property they share.":
        "1 point : une propriété concrète et précise qu'ils ont en commun.",
    "0 points: a difference, something only one has, or a vague/wrong answer.":
        "0 point : une différence, un trait d'un seul, ou une réponse vague ou fausse.",
    "Adults start at item 4. If either of the first two isn't perfect, earlier items are given in reverse.":
        "Les adultes commencent à l'item 4. Si l'un des deux premiers n'est pas parfait, on reprend les items "
        "précédents à rebours.",
    "Discontinue after 3 consecutive scores of 0. No time limit.":
        "Arrêt après 3 notes de 0 consécutives. Pas de limite de temps.",
    "Discontinue after 3 consecutive scores of 0.": "Arrêt après 3 notes de 0 consécutives.",
    "Three tasks: Forward (same order), Backward (reverse), Sequencing (lowest to highest).":
        "Trois tâches : ordre direct, ordre inverse, ordre croissant.",
    "Digits are presented at a rate of one per second and never repeated.":
        "Les chiffres sont dits à raison d'un par seconde, jamais répétés.",
    "Each span length has two trials; each correct trial earns 1 point.":
        "Deux essais par longueur ; chaque essai réussi rapporte 1 point.",
    "A task stops when both trials of the same length are failed.":
        "Une tâche s'arrête si les deux essais d'une longueur sont échoués.",
    "Each task begins with a sample trial that isn't scored.":
        "Chaque tâche commence par un essai d'exemple non noté.",
    "Look at an incomplete matrix or analogy and pick the option that completes it.":
        "Observer une matrice ou une analogie incomplète et choisir la réponse qui la complète.",
    "Rules can act along rows, columns, or both: shape, colour, number, size, fill, rotation.":
        "Les règles portent sur les lignes, les colonnes ou les deux : forme, couleur, nombre, taille, remplissage, "
        "rotation.",
    "There are five response options; exactly one is correct. 1 point each.":
        "Cinq réponses sont proposées ; une seule est juste. 1 point par item.",
    "No strict limit, but examiners prompt after about 30 seconds.":
        "Pas de limite stricte, mais l'examinateur relance après 30 secondes environ.",
    "Adults start at item 4; reversal rule applies.":
        "Les adultes commencent à l'item 4 ; règle du retour en arrière.",
    "You are asked \"What does ___ mean?\" and give a definition.":
        "On vous demande « Que veut dire ___ ? » et vous donnez une définition.",
    "2 points: a precise definition capturing the word's central meaning.":
        "2 points : une définition précise, qui rend le sens central du mot.",
    "1 point: a vague, partial, or overly narrow definition (e.g. one example use).":
        "1 point : une définition vague, partielle ou trop étroite (par exemple, un seul exemple d'emploi).",
    "0 points: a wrong or unrelated meaning.": "0 point : un sens faux ou sans rapport.",
    "Adults start at item 5; reversal rule applies.":
        "Les adultes commencent à l'item 5 ; règle du retour en arrière.",
    "Word problems are read aloud and solved in your head — no paper or pencil.":
        "Les problèmes sont lus à voix haute et résolus de tête, sans papier.",
    "30-second limit per item, timed from the end of the reading.":
        "30 secondes par item, chronométrées à partir de la fin de la lecture.",
    "You may ask for the problem to be repeated once; the timer keeps running.":
        "On peut réentendre le problème une fois ; le chronomètre continue.",
    "1 point for each correct answer.": "1 point par bonne réponse.",
    "Adults start at item 6; reversal rule applies.":
        "Les adultes commencent à l'item 6 ; règle du retour en arrière.",
    "Each row shows two target symbols and a search group of five.":
        "Chaque ligne : deux symboles cibles et un groupe de cinq symboles.",
    "Mark YES if either target appears in the search group, NO if neither does.":
        "OUI si l'une des cibles est dans le groupe, NON si aucune n'y est.",
    "Distractors are deliberately similar: mirrored, rotated or one stroke different.":
        "Distracteurs volontairement proches : en miroir, tournés ou à un trait près.",
    "120-second limit. Work in order without skipping.": "120 secondes. Travailler dans l'ordre, sans sauter de ligne.",
    "Score = correct answers minus incorrect answers.": "Note = bonnes réponses moins mauvaises réponses.",
    "Choose the three pieces that, put together, make the puzzle.":
        "Choisir les trois pièces qui, assemblées, forment le puzzle.",
    "Pieces may need to be rotated (turned), but never flipped over.":
        "Les pièces peuvent devoir être tournées, mais jamais retournées.",
    "Exactly three pieces; all three must be correct to earn the 1 point.":
        "Exactement trois pièces ; les trois doivent être justes pour obtenir le point.",
    "30-second time limit per item.": "30 secondes par item.",
    "General-knowledge questions on a wide range of topics.": "Des questions de culture générale sur des sujets très variés.",
    "Adults start at item 3; reversal rule applies.":
        "Les adultes commencent à l'item 3 ; règle du retour en arrière.",
    "A key pairs each digit 1–9 with a unique symbol.": "Une clé associe à chaque chiffre de 1 à 9 un symbole unique.",
    "On the real test you draw the matching symbol under each digit.":
        "Dans le vrai test, on dessine le symbole correspondant sous chaque chiffre.",
    "120-second limit. Work in order — skipping is not allowed.":
        "120 secondes. Travailler dans l'ordre — interdit de sauter une case.",
    "Score = number of correct responses (max 135).": "Note = nombre de bonnes réponses (135 au maximum).",

    # ---------------------------------------------------------------- how to play here
    "Click or tap a block to turn it to its next face; right-click or the scroll wheel turns it back.":
        "Clic ou toucher sur un cube : face suivante. Clic droit ou molette : face précédente.",
    "The design is checked automatically. Space or the Give up button skips an item.":
        "Le motif est vérifié automatiquement. Espace ou le bouton Passer sautent l'item.",
    "Pick the answer an examiner would score highest.": "Choisissez la réponse qu'un examinateur noterait le mieux.",
    "Click an answer or press 1–4.": "Cliquez sur une réponse ou appuyez sur 1–4.",
    "Listen to the digits (they are also shown), then type your answer and press Enter.":
        "Écoutez les chiffres (ils sont aussi affichés), puis tapez votre réponse et appuyez sur Entrée.",
    "Backspace corrects. The answer submits automatically at full length.":
        "Retour arrière corrige. La réponse est validée d'elle-même quand elle est complète.",
    "Click an option or press 1–5.": "Cliquez sur une réponse ou appuyez sur 1–5.",
    "Choose the definition that would earn the most credit.": "Choisissez la définition qui rapporterait le plus de points.",
    "The problem is shown while it's 'read', then hidden.": "Le problème est affiché pendant sa « lecture », puis masqué.",
    "Type your answer and press Enter.  R repeats the problem once.":
        "Tapez votre réponse et appuyez sur Entrée.  R répète le problème une fois.",
    "YES:  Y  or  ←        NO:  N  or  →": "OUI :  Y  ou  ←        NON :  N  ou  →",
    "Or click the buttons.": "Ou cliquez sur les boutons.",
    "Click pieces (or press 1–6) to select three, then press Enter.":
        "Cliquez sur les pièces (ou appuyez sur 1–6) pour en choisir trois, puis appuyez sur Entrée.",
    "Here the lookup is reversed: each box shows a symbol. Find it in the key and type its digit (1–9), or tap "
    "it in the key. The key is new every session.":
        "Ici, chaque case montre un symbole : tapez son chiffre (1–9) d'après la clé, ou touchez-le dans la "
        "clé. Nouvelle clé à chaque séance.",

    # ---------------------------------------------------------------- subtest briefing
    "Begin": "Commencer",
    "Abandon assessment": "Quitter l'évaluation",
    "Back": "Retour",
    "Rated set": "Série classée",
    "Rated set  ·  {rating}": "Série classée  ·  {rating}",
    "Rules of the real test": "Règles du vrai test",
    "How to play": "Comment jouer",
    "DAILY CHALLENGE #{n}  ·  SAME PUZZLES FOR EVERYONE TODAY":
        "DÉFI DU JOUR N° {n}  ·  LES MÊMES PUZZLES POUR TOUT LE MONDE AUJOURD'HUI",
    "FULL ASSESSMENT  ·  SUBTEST {n} OF {total}": "ÉVALUATION COMPLÈTE  ·  ÉPREUVE {n} SUR {total}",
    "RULES OF THE REAL TEST": "RÈGLES DU VRAI TEST",
    "HOW TO PLAY HERE": "COMMENT JOUER ICI",
    "MODE": "MODE",
    "10 puzzles matched to your rating": "10 puzzles adaptés à votre cote",
    "You've already played today ({solved}/10). This run is practice and won't change your result.":
        "Vous avez déjà joué aujourd'hui ({solved}/10). Cette partie d'entraînement ne changera pas votre résultat.",
    "Daily challenge: 10 puzzles from easy to beyond the real test's hardest item, with feedback after each. "
    "Only your first completed try today counts.":
        "Défi du jour : 10 puzzles, du plus facile à plus dur que le vrai test, avec un retour après chacun. "
        "Seul votre premier essai terminé aujourd'hui compte.",
    "Test conditions: no feedback, exactly like the real assessment. Your result stays hidden until all ten "
    "subtests are complete.":
        "Conditions de test : aucun retour, exactement comme lors de la vraie évaluation. Votre résultat reste "
        "masqué jusqu'à la fin des dix épreuves.",
    "Training: after every item you'll see the score it earned and the best answer.":
        "Entraînement : après chaque item, vous verrez les points obtenus et la meilleure réponse.",
    "Test conditions: no feedback after items. Sample items are still explained.":
        "Conditions de test : aucun retour après les items. Les items d'exemple restent expliqués.",

    # ---------------------------------------------------------------- during a subtest
    "Pause": "Pause",
    "Pause  (Esc)": "Pause  (Échap)",
    "DISCONTINUE": "ARRÊT",
    "Stops after {n} consecutive scores of 0": "S'arrête après {n} notes de 0 consécutives",
    "Stops after 2 consecutive scores of 0": "S'arrête après 2 notes de 0 consécutives",
    "{set}  ·  puzzle {position} of {length}  ·  level {level}": "{set}  ·  puzzle {position} sur {length}  ·  niveau {level}",
    "  (beyond the real test)": "  (au-delà du vrai test)",
    "Sample item": "Item d'exemple",
    "Item {item} of {items}": "Item {item} sur {items}",
    "  ·  reverse order": "  ·  ordre inverse",
    "Rating {rating}  ·  puzzles adapt to your rating":
        "Cote {rating}  ·  les puzzles s'adaptent à votre cote",
    "Same puzzles for everyone today  ·  easy to brutal":
        "Les mêmes puzzles pour tous aujourd'hui  ·  de facile à redoutable",
    "Perfect": "Parfait",
    "Partial credit": "Points partiels",
    "No credit": "Aucun point",
    "   (sample, not scored)": "   (exemple, non noté)",
    "Enter to continue": "Entrée pour continuer",
    "Tap to continue": "Touchez pour continuer",
    "Time limit reached.": "Temps écoulé.",
    "Correct!": "Correct !",
    "Not quite — ": "Pas tout à fait — ",
    "check the key and try again.": "vérifiez la clé et réessayez.",
    "find the symbol in the key above.": "cherchez le symbole dans la clé au-dessus.",
    "a target IS in the group.": "une cible EST dans le groupe.",
    "neither target appears exactly.": "aucune cible n'y figure à l'identique.",
    "Practice": "Exercice",
    "Ready": "Prêt",
    ("{n} answered", "{n} answered"): ("{n} réponse", "{n} réponses"),
    ("Practice — {n} correct answer to go. Not timed.", "Practice — {n} correct answers to go. Not timed."):
        ("Exercice — encore {n} bonne réponse. Sans chronomètre.",
         "Exercice — encore {n} bonnes réponses. Sans chronomètre."),
    "{seconds}-second limit  ·  work fast, but accurately": "Limite de {seconds} secondes  ·  allez vite, mais sans erreur",
    "Practice complete": "Exercice terminé",
    "The {seconds}-second timer starts as soon as you continue.":
        "Le chronomètre de {seconds} secondes démarre dès que vous continuez.",
    "No feedback is given during the timed section.": "Aucun retour n'est donné pendant la partie chronométrée.",
    "Press Space to begin": "Appuyez sur Espace pour commencer",
    "Tap to begin": "Touchez pour commencer",
    "your answer": "votre réponse",
    "Del": "Effacer",

    # verbal
    ("{n} pt", "{n} pts"): ("{n} pt", "{n} pts"),
    "correct": "juste",
    "Best answer: {answer}": "Meilleure réponse : {answer}",
    "Abstract category — exactly what earns full credit.":
        "Catégorie abstraite — exactement ce qui rapporte tous les points.",
    "True, but concrete. 2-point answer: {answer}": "Vrai, mais concret. Pour 2 points : {answer}",
    "A 2-point answer: {answer}": "Réponse à 2 points : {answer}",
    "In what way are they alike?": "En quoi se ressemblent-ils ?",
    "Precise definition — full credit.": "Définition précise — tous les points.",
    "Vague or partial. Precise: {answer}": "Vague ou partielle. Précise : {answer}",
    "Meaning: {answer}": "Sens : {answer}",
    "What does": "Que veut dire le mot",
    "mean?": "Choisissez la meilleure définition.",
    "Answer: {answer}": "Réponse : {answer}",

    # arithmetic
    "Repeat": "Répéter",
    "Repeat  (R)": "Répéter  (R)",
    "Problem hidden — solve it in your head": "Problème masqué — résolvez-le de tête",
    "(tap Repeat to see it once more)": "(touchez Répéter pour le revoir une fois)",
    "(press R to hear it once more)": "(appuyez sur R pour le réentendre une fois)",
    "(already repeated)": "(déjà répété)",
    "Time limit reached. Answer: {answer}": "Temps écoulé. Réponse : {answer}",
    "apples": "pommes",
    "pencils": "crayons",
    "stickers": "vignettes",
    "books": "livres",
    "marbles": "billes",
    "cookies": "biscuits",
    "stamps": "timbres",
    "cards": "cartes",
    "passengers": "passagers",
    "hours": "heures",
    "days": "jours",
    "minutes": "minutes",
    "years": "ans",
    "one-half": "la moitié",
    "one-third": "le tiers",
    "{name} has {a} {things} and gets {b} more. How many {things} does {name} have now?":
        "{name} a {a} {things} et en reçoit {b} de plus. Combien de {things} a maintenant {name} ?",
    "{name} had {a} {things} and gave away {b}. How many are left?":
        "{name} avait {a} {things} et en a donné {b}. Combien en reste-t-il ?",
    "There are {a} bags with {b} {things} in each bag. How many {things} are there in all?":
        "Il y a {a} sacs avec {b} {things} dans chaque sac. Combien de {things} y a-t-il en tout ?",
    "Notebooks cost {price} each. How much do {n} notebooks cost?":
        "Un cahier coûte {price}. Combien coûtent {n} cahiers ?",
    "{name} shares {cookies} equally among {per} friends. How many does each friend get?":
        "{name} partage {cookies} à parts égales entre {per} amis. Combien chaque ami en reçoit-il ?",
    "A bus has {passengers}. At the next stop, {b} more get on. How many passengers are on the bus?":
        "Un bus transporte {passengers}. À l'arrêt suivant, {b} autres montent. Combien de passagers y a-t-il "
        "dans le bus ?",
    "{name} buys a toy for {cost} and pays with a {pay} bill. How much change does {name} get?":
        "{name} achète un jouet à {cost} et paie avec un billet de {pay}. Combien de monnaie rend-on à {name} ?",
    "{name} buys {n} sandwiches at {price} each and pays with a {pay} bill. How much change does {name} receive?":
        "{name} achète {n} sandwichs à {price} pièce et paie avec un billet de {pay}. Combien de monnaie "
        "lui rend-on ?",
    "A car travels at {speed}. How far does it travel in {hours}?":
        "Une voiture roule à {speed}. Combien de kilomètres parcourt-elle en {hours} ?",
    "{name} reads {per_day} pages every day. How many pages does {name} read in {days}?":
        "{name} lit {per_day} pages par jour. Combien de pages lit {name} en {days} ?",
    "{name} has {marbles} and gives {fraction} of them to a friend. How many marbles does {name} have left?":
        "{name} a {marbles} et en donne {fraction} à un ami. Combien de billes reste-t-il à {name} ?",
    "A jacket costs {price}. It is on sale for {pct}% off. What is the sale price?":
        "Une veste coûte {price}. Elle est soldée à −{pct} %. Quel est son prix soldé ?",
    "{workers} workers can paint a house in {hours}. At the same rate, how many hours would it take {new} workers?":
        "{workers} ouvriers peuvent peindre une maison en {hours}. Au même rythme, combien d'heures faudrait-il à "
        "{new} ouvriers ?",
    "{name} scores {a}, {b} and {c} on three tests. What is {name}'s average score?":
        "{name} obtient {a}, {b} et {c} points à trois contrôles. Quelle est la moyenne de {name} ?",
    "A machine fills {rate} bottles every minute. How many bottles does it fill in {minutes}?":
        "Une machine remplit {rate} bouteilles par minute. Combien de bouteilles remplit-elle en {minutes} ?",
    "After a {inc}% price increase, a lamp costs {price}. What did it cost before the increase?":
        "Après une hausse de {inc} %, une lampe coûte {price}. Combien coûtait-elle avant la hausse ?",
    "{name} and a friend split some money in the ratio {a} to {b}. If {name} gets {share}, how much money was "
    "there in total?":
        "{name} et un ami se partagent une somme dans le rapport {a} à {b}. Si {name} reçoit {share}, quelle était "
        "la somme totale ?",
    "A train travels {distance} at {speed1}, then returns at {speed2}. How many hours does the round trip take?":
        "Un train parcourt {distance} à {speed1}, puis revient à {speed2}. Combien d'heures dure l'aller-retour ?",
    "The average of {n} numbers is {avg}. When one number, {drop}, is removed, what is the sum of the remaining "
    "numbers?":
        "La moyenne de {n} nombres est {avg}. Si l'on retire l'un d'eux, {drop}, quelle est la somme des nombres "
        "restants ?",
    "A bike that costs {price} goes up in price by 10%, then the new price is cut by 10%. What does it cost now?":
        "Un vélo qui coûte {price} augmente de 10 %, puis le nouveau prix baisse de 10 %. Combien coûte-t-il "
        "maintenant ?",
    "One pipe fills a tank in {a}, another in {b}. How many hours do they take working together?":
        "Un robinet remplit une cuve en {a}, un autre en {b}. En combien d'heures la remplissent-ils ensemble ?",
    "{name} is three times as old as a cousin. In {years}, {name} will be twice as old as the cousin. How old is "
    "the cousin now?":
        "{name} a trois fois l'âge de son cousin. Dans {years}, {name} aura deux fois l'âge du cousin. Quel âge a "
        "le cousin aujourd'hui ?",
    "Half of a number plus a third of the same number is {sum}. What is the number?":
        "La moitié d'un nombre plus le tiers de ce même nombre font {sum}. Quel est ce nombre ?",
    "Two cyclists start {distance} apart and ride towards each other at {speed1} and {speed2}. After how many "
    "hours do they meet?":
        "Deux cyclistes partent à {distance} l'un de l'autre et roulent l'un vers l'autre à {speed1} et {speed2}. "
        "Au bout de combien d'heures se croisent-ils ?",

    # digit span
    "Forward": "Ordre direct",
    "Backward": "Ordre inverse",
    "Sequencing": "Ordre croissant",
    "Repeat the digits in the same order.": "Répétez les chiffres dans le même ordre.",
    "Repeat the digits in reverse order.": "Répétez les chiffres dans l'ordre inverse.",
    "Repeat the digits in order from lowest to highest.": "Répétez les chiffres du plus petit au plus grand.",
    "{task}  ·  sample": "{task}  ·  exemple",
    "{task}  ·  {length} digits  ·  trial {trial} of 2": "{task}  ·  {length} chiffres  ·  essai {trial} sur 2",
    "Score {score}": "Score {score}",
    "Digit Span {task}": "Mémoire des chiffres : {task}",
    "e.g.  {example}": "ex. :  {example}",
    "Press Space when ready": "Appuyez sur Espace quand vous êtes prêt",
    "Tap anywhere when ready": "Touchez l'écran quand vous êtes prêt",
    "Listen…": "Écoutez…",
    "Correct": "Juste",
    "Incorrect": "Faux",
    "  (sample — not scored)": "  (exemple — non noté)",
    "Presented: {shown}     Answer: {answer}": "Présenté : {shown}     Réponse : {answer}",
    "Each task stops when both trials of one length are failed":
        "Chaque tâche s'arrête quand les deux essais d'une même longueur sont échoués",

    # block design
    "Give up": "Passer",
    "Give up  (Space)": "Passer  (Espace)",
    "Item abandoned.": "Item abandonné.",
    "Completed in {seconds} s — speed bonus +{bonus}": "Terminé en {seconds} s — bonus de rapidité +{bonus}",
    "Completed in {seconds} s": "Terminé en {seconds} s",
    "MODEL": "MODÈLE",
    "YOUR BLOCKS": "VOS CUBES",
    "The model is on the left — compare edge by edge.": "Le modèle est à gauche — comparez bord à bord.",

    # matrix reasoning, visual puzzles, speed
    "The answer was option {option}.": "La bonne réponse était la {option}.",
    "Confirm": "Valider",
    "Confirm  (Enter)": "Valider  (Entrée)",
    "Correct pieces: {pieces}": "Pièces justes : {pieces}",
    "Time limit reached. Correct pieces: {pieces}": "Temps écoulé. Pièces justes : {pieces}",
    "PUZZLE": "PUZZLE",
    ("Select {n} more piece", "Select {n} more pieces"):
        ("Choisissez encore {n} pièce", "Choisissez encore {n} pièces"),
    "YES": "OUI",
    "NO": "NON",
    "TARGETS": "CIBLES",
    "SEARCH GROUP": "GROUPE DE RECHERCHE",
    "KEY": "CLÉ",

    # ---------------------------------------------------------------- results
    "Train again": "Recommencer",
    "Skill tree": "Accueil",
    "SCALED SCORE": "NOTE STANDARD",
    "Raw {raw} / {max}   ·   ≈ {percentile}th percentile   ·   mean is 10, SD 3":
        "Note brute {raw} / {max}   ·   ≈ {percentile}e centile   ·   moyenne 10, écart type 3",
    "NEW PERSONAL BEST": "NOUVEAU RECORD PERSONNEL",
    "Done": "Terminé",
    "SUBTEST COMPLETE": "ÉPREUVE TERMINÉE",
    "Scores are hidden. You can show them in Settings.":
        "Les scores sont masqués. Vous pouvez les afficher dans les paramètres.",
    "Forward {forward}  ·  Backward {backward}  ·  Sequencing {sequencing}":
        "Direct {forward}  ·  Inverse {backward}  ·  Croissant {sequencing}",
    "{correct} correct  ·  {wrong} incorrect  ·  {attempted} attempted":
        "{correct} justes  ·  {wrong} fausses  ·  {attempted} tentées",
    ("Stopped after {n} item. Every subtest ends after a run of misses, so everyone reaches that point.",
     "Stopped after {n} items. Every subtest ends after a run of misses, so everyone reaches that point."):
        ("Arrêt après {n} item. Chaque épreuve s'arrête après une série d'échecs, donc tout le monde atteint ce "
         "point.",
         "Arrêt après {n} items. Chaque épreuve s'arrête après une série d'échecs, donc tout le monde atteint ce "
         "point."),
    ("{n} item given, right to the end of the subtest", "{n} items given, right to the end of the subtest"):
        ("{n} item donné, jusqu'à la fin de l'épreuve", "{n} items donnés, jusqu'à la fin de l'épreuve"),
    "ASSESSMENT COMPLETE": "ÉVALUATION TERMINÉE",
    "Your skill constellation": "Votre constellation de compétences",
    "ALL TEN SUBTESTS DONE": "LES DIX ÉPREUVES SONT TERMINÉES",
    "You finished a full assessment under real test conditions: no feedback, real time limits, real stopping "
    "rules. That's the whole experience.":
        "Vous avez terminé une évaluation complète dans les conditions réelles : aucun retour, de vrais temps "
        "limites, de vraies règles d'arrêt. C'est toute l'expérience.",
    "Scores are hidden. Your results are saved, and you can show them any time in Settings.":
        "Les scores sont masqués. Vos résultats sont enregistrés, et vous pouvez les afficher à tout moment dans "
        "les paramètres.",
    "≈ {percentile}th percentile": "≈ {percentile}e centile",
    "NOT AN ACTUAL IQ TEST": "CE N'EST PAS UN VRAI TEST DE QI",
    "Estimates use approximate norms made up for this game. They show trends in your training, not a real IQ.":
        "Estimations fondées sur des normes inventées pour ce jeu : elles suivent vos progrès, pas un vrai QI.",
    "tap to skip": "touchez pour passer",
    "click to skip": "cliquez pour passer",
    "Paused": "En pause",
    "Timers are stopped (the real test can't be paused!)  ·  F11 toggles fullscreen":
        "Les chronomètres sont arrêtés (le vrai test, lui, ne s'arrête pas !)  ·  F11 bascule en plein écran",
    "Resume": "Reprendre",
    "Restart subtest": "Recommencer l'épreuve",
    "Quit to skill tree": "Revenir à l'accueil",
    "Another set": "Une autre série",
    "Copy result": "Copier le résultat",
    "Copied! Paste it anywhere to share.": "Copié ! Collez-le où vous voulez pour le partager.",
    "Couldn't reach the clipboard.": "Impossible d'accéder au presse-papiers.",
    "Daily #{n}": "Défi du jour n° {n}",
    "Puzzleth Daily #{n} · {subtest}": "Puzzleth, défi du jour n° {n} · {subtest}",
    "PUZZLE RATING": "COTE PUZZLES",
    "{solved} of {length} solved": "{solved} sur {length} résolus",
    ("{n} puzzle played", "{n} puzzles played"): ("{n} puzzle joué", "{n} puzzles joués"),
    "  ·  peak {peak}": "  ·  record {peak}",
    "  ·  #{rank} of {total} online": "  ·  {rank}e sur {total} en ligne",
    "SOLVED": "RÉSOLUS",
    ("Daily streak: {n} day", "Daily streak: {n} days"):
        ("Série quotidienne : {n} jour", "Série quotidienne : {n} jours"),
    "Practice replay  ·  today's result was {solved}/10":
        "Partie d'entraînement  ·  le résultat du jour était de {solved}/10",
    "difficulty level of each puzzle": "niveau de difficulté de chaque puzzle",

    # ---------------------------------------------------------------- players and names
    "Restore a player": "Restaurer un joueur",
    "Cancel": "Annuler",
    "A new player starts with fresh progress and their own settings.":
        "Un nouveau joueur part de zéro, avec ses propres paramètres.",
    "Your progress so far will be kept under this name.": "Votre progression actuelle sera conservée sous ce nom.",
    "Your progress is saved under this name. Everyone else can add their own.":
        "Votre progression est enregistrée sous ce nom. Les autres peuvent ajouter le leur.",
    "Tap the letters, then OK": "Touchez les lettres, puis OK",
    "Type your name, or pick each letter with Up/Down and lock it in with Right":
        "Tapez votre nom, ou choisissez chaque lettre avec Haut/Bas et validez-la avec Droite",
    "ENTER YOUR NAME": "ENTREZ VOTRE NOM",
    "Enter at least one letter": "Entrez au moins une lettre",
    "{name} is already a player here": "{name} est déjà un joueur ici",
    "There can be at most {n} players": "Il ne peut y avoir que {n} joueurs au maximum",
    "There's already a player called {name} here. Remove them first.":
        "Il y a déjà un joueur nommé {name} ici. Supprimez-le d'abord.",
    "Enter all {n} characters of the code": "Entrez les {n} caractères du code",
    "Enter the recovery code from Leaderboard > Move to another device on your other device.":
        "Entrez le code de récupération affiché dans Classement > Passer sur un autre appareil, sur votre autre "
        "appareil.",
    "Restoring…": "Restauration…",
    "Tap the characters, then OK": "Touchez les caractères, puis OK",
    "Type or paste the code, then press Enter": "Tapez ou collez le code, puis appuyez sur Entrée",
    "RESTORE A PLAYER": "RESTAURER UN JOUEUR",
    "Not played yet": "Pas encore joué",
    "Last played today": "A joué aujourd'hui",
    "Last played yesterday": "A joué hier",
    ("Last played {n} day ago", "Last played {n} days ago"):
        ("A joué il y a {n} jour", "A joué il y a {n} jours"),
    "New player": "Nouveau joueur",
    "Remove…": "Supprimer…",
    "Done removing": "Fin de la suppression",
    "Restore…": "Restaurer…",
    "WHO'S PLAYING?": "QUI JOUE ?",
    "Tap a player twice to remove them and all their progress.":
        "Touchez deux fois un joueur pour le supprimer avec toute sa progression.",
    "Choose your name. Each player keeps their own progress and settings.":
        "Choisissez votre nom. Chaque joueur garde sa propre progression et ses propres paramètres.",
    "Tap again to remove": "Touchez à nouveau pour supprimer",
    "all of this player's progress": "toute la progression de ce joueur",
    "{n} / 10 skills measured": "{n} / 10 compétences mesurées",
    "Playing now": "Joue en ce moment",

    # ---------------------------------------------------------------- leaderboard and moving devices
    "Play a rated set": "Jouer une série classée",
    "Move to another device": "Passer sur un autre appareil",
    "Tap again to leave": "Touchez à nouveau pour quitter",
    "Leave the leaderboard": "Quitter le classement",
    "Joining…": "Inscription…",
    "Join as {name}": "Rejoindre en tant que {name}",
    "LEADERBOARD": "CLASSEMENT",
    "Puzzle ratings from rated sets, from players everywhere. You're ranked after your first set.":
        "Les cotes obtenues en séries classées par des joueurs du monde entier. Vous êtes classé après votre première "
        "série.",
    "PLAYER": "JOUEUR",
    "RATING": "COTE",
    "PUZZLES": "PUZZLES",
    "Loading…": "Chargement…",
    "Nobody is ranked yet. Play a rated set to be the first!":
        "Personne n'est encore classé. Jouez une série classée pour être le premier !",
    "COMPETE ONLINE": "JOUER EN LIGNE",
    "Put {name}'s puzzle ratings on the leaderboard.": "Publier les cotes de {name} dans le classement en ligne.",
    "Your name, ratings and progress are sent. The progress is a backup that lets you move to another device "
    "with a recovery code. Leave any time to delete it all from the server.":
        "Votre nom, vos cotes et votre progression sont envoyés. La progression est une sauvegarde qui vous "
        "permet de passer sur un autre appareil avec un code de récupération. Quittez le classement à tout moment "
        "pour tout effacer du serveur.",
    "YOU": "VOUS",
    "of {total} ranked in {subtest}": "sur {total} classés en {subtest}",
    "Unranked": "Non classé",
    ("{n} more puzzle to be ranked", "{n} more puzzles to be ranked"):
        ("Encore {n} puzzle pour être classé", "Encore {n} puzzles pour être classé"),
    "Your rating is on its way": "Votre cote arrive",
    "Unrated": "Sans cote",
    "Play a {subtest} rated set to get a rating": "Jouez une série classée en {subtest} pour obtenir une cote",
    "Rating {rating}  ·  peak {peak}": "Cote {rating}  ·  record {peak}",
    "Copy": "Copier",
    "New code": "Nouveau code",
    "Tap again": "Touchez à nouveau",
    "Copied!": "Copié !",
    "Couldn't reach the clipboard. Write the code down instead.":
        "Impossible d'accéder au presse-papiers. Notez plutôt le code.",
    "MOVE TO ANOTHER DEVICE": "PASSER SUR UN AUTRE APPAREIL",
    "{name}'S RECOVERY CODE": "CODE DE RÉCUPÉRATION DE {name}",
    "Getting your code…": "Récupération de votre code…",
    "No code yet": "Pas encore de code",
    "Your current code will stop working.": "Votre code actuel ne fonctionnera plus.",
    "On your other device, choose Restore a player when it asks for a name (or on the Who's playing screen) "
    "and enter this code.":
        "Sur votre autre appareil, choisissez Restaurer un joueur quand il vous demande un nom (ou depuis l'écran "
        "Qui joue ?) et entrez ce code.",
    "{name}'s progress, settings and leaderboard place move there. This device keeps its copy of the progress "
    "but stops posting to the leaderboard.":
        "La progression, les paramètres et la place au classement de {name} y sont transférés. Cet appareil "
        "garde sa copie de la progression, mais n'envoie plus rien au classement.",
    "Keep the code private: anyone who has it can take over this player. If someone else has seen it, get a new "
    "code.":
        "Gardez ce code pour vous : quiconque le possède peut prendre le contrôle de ce joueur. Si quelqu'un "
        "d'autre l'a vu, demandez un nouveau code.",
    "Couldn't reach the leaderboard. Check your connection and try again.":
        "Impossible de joindre le classement. Vérifiez votre connexion et réessayez.",
    "Too many wrong codes from here today. Try again tomorrow.":
        "Trop de codes erronés depuis cet endroit aujourd'hui. Réessayez demain.",
    "Too many new players from here today. Try again tomorrow.":
        "Trop de nouveaux joueurs depuis cet endroit aujourd'hui. Réessayez demain.",
    "The leaderboard said no ({error}).": "Le classement a refusé ({error}).",
    "The leaderboard's address, {address}, isn't a web address (see server/README.md).":
        "L'adresse du classement, {address}, n'est pas une adresse web (voir server/README.md).",
    "No player has that code. Check it and try again.": "Aucun joueur n'a ce code. Vérifiez-le et réessayez.",

    # ---------------------------------------------------------------- learn
    "Start the assessment": "Commencer l'évaluation",
    "Next": "Suivant",
    "Previous": "Précédent",
    "Next topic": "Sujet suivant",
    "Skip": "Passer",
    "BEFORE YOUR FIRST FULL ASSESSMENT": "AVANT VOTRE PREMIÈRE ÉVALUATION COMPLÈTE",
    "A quick look at what a real session is like. Skip whenever you like.":
        "Un aperçu rapide d'une vraie séance. Vous pouvez passer à tout moment.",
    "LEARN": "APPRENDRE",
    "How the WAIS works, what a session is like, and how to read the scores":
        "Comment fonctionne la WAIS, comment se passe une séance et comment lire les scores",

    # ---------------------------------------------------------------- settings
    "SETTINGS": "PARAMÈTRES",
    "Feedback while training": "Retour pendant l'entraînement",
    "After each item, show how it was scored and the best answer. The full assessment never gives feedback, "
    "just like the real test.":
        "Après chaque item, montrer les points obtenus et la meilleure réponse. L'évaluation complète ne donne "
        "jamais de retour, comme le vrai test.",
    "Test-style scores": "Scores de type test",
    "Show scaled scores, index scores and the Full Scale Score. Hide them to practise without a number. Puzzle "
    "ratings and daily results still show.":
        "Notes standard, indices et score global. Masquez-les pour vous entraîner sans chiffres : les cotes et "
        "le défi du jour restent affichés.",
    "Sound effects": "Effets sonores",
    "Clicks, timer ticks and the spoken digits in Digit Span. Right/wrong chimes only play when feedback is "
    "shown.":
        "Clics, tic-tac du chronomètre et chiffres prononcés de Mémoire des chiffres. Les sons juste/faux ne "
        "jouent que si le retour est activé.",
    "No audio device was found.": "Aucun périphérique audio n'a été trouvé.",
    "Music": "Musique",
    ("Plays the {n} track in your music folder on a shuffled loop. It turns down while digits are read out.",
     "Plays the {n} tracks in your music folder on a shuffled loop. It turns down while digits are read out."):
        ("Joue en boucle aléatoire le morceau de votre dossier de musique. Le volume baisse pendant la lecture "
         "des chiffres.",
         "Joue en boucle aléatoire les {n} morceaux de votre dossier de musique. Le volume baisse pendant la "
         "lecture des chiffres."),
    "Put your own mp3, ogg or wav files in the puzzleth/music folder. None found yet.":
        "Placez vos fichiers mp3, ogg ou wav dans le dossier puzzleth/music. Aucun trouvé pour l'instant.",
    "Put your own mp3, ogg or wav files in the puzzleth/music folder or ~/.puzzleth/music. None found yet.":
        "Placez vos fichiers mp3, ogg ou wav dans le dossier puzzleth/music ou ~/.puzzleth/music. Aucun trouvé "
        "pour l'instant.",
    "Fullscreen  (F11)": "Plein écran  (F11)",
    "Use your browser's menu to go fullscreen, or add Puzzleth to your home screen.":
        "Passez en plein écran depuis le menu du navigateur, ou ajoutez Puzzleth à votre écran d'accueil.",
    "Fill the whole screen. In a window, the game scales to any size you like.":
        "Occuper tout l'écran. Dans une fenêtre, le jeu s'adapte à la taille de votre choix.",
    "On": "Activé",
    "Off": "Désactivé",
    "Shown": "Affichés",
    "Hidden": "Masqués",
}

STRINGS = {key: tuple(map(spacing, value)) if isinstance(value, tuple) else spacing(value)
           for key, value in STRINGS.items()}
