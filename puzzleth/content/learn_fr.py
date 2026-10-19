"""The Learn screen in French: learn.py translated, with the same topics and pages."""
from ..locales.fr import spacing

EXPECT = [
    ("Avant la séance", [
        "Une évaluation cognitive est une séance individuelle avec un psychologue ou un examinateur formé. Les "
        "épreuves principales durent en général entre une heure et une heure et demie, parfois dans le cadre "
        "d'un bilan plus long.",
        "Il n'y a rien à réviser et rien à apporter, sauf vos lunettes ou vos appareils auditifs si vous en "
        "portez. Le sommeil, les repas et vos traitements habituels comptent plus que n'importe quelle "
        "préparation.",
        "C'est normal d'être stressé. Les examinateurs voient des personnes stressées tous les jours, et les "
        "premiers items de chaque épreuve sont faciles exprès, en partie pour vous aider à vous mettre à l'aise.",
        "Vous pouvez poser des questions avant de commencer, et demander une courte pause entre deux épreuves.",
    ]),
    ("Le rôle de l'examinateur", [
        "## Il lit un texte standardisé",
        "Les consignes sont lues mot pour mot, pour que tout le monde passe exactement le même test. C'est pour "
        "cela qu'elles peuvent paraître formelles.",
        "## Il ne vous dira pas si vous avez juste",
        "C'est ce qui déstabilise le plus. Un visage neutre ou un simple « d'accord » après chaque réponse est la "
        "règle pour tout le monde. Ce n'est pas le signe que vous vous êtes trompé.",
        "## Il vous chronomètre et prend des notes",
        "Un chronomètre est utilisé ouvertement pour les épreuves minutées, et les réponses orales sont notées "
        "mot pour mot. C'est aussi la procédure normale.",
        "## Il peut demander « Pouvez-vous m'en dire plus ? »",
        "Dans les épreuves verbales, une réponse vague est suivie d'une relance neutre. Cela veut dire que la "
        "réponse pourrait rapporter plus de points si vous l'expliquez davantage, pas qu'elle était fausse.",
    ]),
    ("Les règles que vous remarquerez", [
        "## Commencer en cours de route",
        "Les adultes commencent en général quelques items après le début de l'épreuve, pas à l'item 1. "
        "L'examinateur sait déjà où.",
        "## Revenir en arrière",
        "Si l'une de vos deux premières réponses n'est pas entièrement juste, l'examinateur revient à des items "
        "plus faciles. C'est la règle du retour en arrière. Elle permet de trouver un point de départ solide, "
        "puis vous obtenez les points de tous les items plus faciles que vous avez sautés.",
        "## S'arrêter après quelques erreurs",
        "Chaque épreuve s'arrête après un certain nombre d'échecs consécutifs (deux ou trois selon l'épreuve). "
        "Tout le monde atteint ce point, car les items deviennent de plus en plus difficiles, jusqu'à l'être "
        "pour presque tout le monde. Cet arrêt fait partie du test, ce n'est pas un échec.",
        "## On a le droit de dire « Je ne sais pas »",
        "Vous pouvez deviner, et vous pouvez aussi passer. On ne s'attend pas à ce que vous répondiez à tout.",
    ]),
    ("Après l'évaluation", [
        "Vos réponses sont comparées à celles d'un grand groupe de personnes de votre âge, puis converties en "
        "scores pour chaque épreuve, pour chacun des quatre domaines et pour l'ensemble.",
        "Un bon compte rendu donne des intervalles, pas seulement des chiffres isolés, et situe les résultats par "
        "rapport à votre parcours, votre scolarité et la raison du bilan. Les chiffres ne sont qu'une pièce d'un "
        "tableau plus large.",
        "Des résultats inégaux sont normaux. La plupart des gens réussissent nettement mieux dans certains "
        "domaines que dans d'autres.",
        "Si vous vous êtes entraîné avec ce jeu ou quelque chose de similaire, dites-le à l'examinateur. "
        "L'entraînement peut légèrement augmenter les scores, et il pourra en tenir compte.",
    ]),
]

SUBTESTS = [
    ("Les dix épreuves  (1 sur 3)", [
        "## Cubes  ·  Raisonnement perceptif",
        "Reproduire un motif rouge et blanc avec des cubes. Évalue la capacité à décomposer une image en parties "
        "puis à la reconstruire, sous la pression du temps.",
        "## Similitudes  ·  Compréhension verbale",
        "« En quoi un piano et une guitare se ressemblent-ils ? » Évalue le raisonnement verbal abstrait : trouver "
        "la catégorie, pas un détail de surface.",
        "## Mémoire des chiffres  ·  Mémoire de travail",
        "Répéter des chiffres à l'endroit, à l'envers et dans l'ordre croissant. Évalue la capacité à garder une "
        "information en tête et à la manipuler.",
        "## Matrices  ·  Raisonnement perceptif",
        "Trouver la pièce manquante d'un motif. Un test classique de raisonnement fluide, c'est-à-dire résoudre "
        "des problèmes nouveaux sans s'appuyer sur ses connaissances.",
    ]),
    ("Les dix épreuves  (2 sur 3)", [
        "## Vocabulaire  ·  Compréhension verbale",
        "Expliquer le sens de mots. La connaissance des mots est l'un des meilleurs prédicteurs du score global.",
        "## Arithmétique  ·  Mémoire de travail",
        "Des problèmes à résoudre de tête. C'est moins une question de niveau en maths que de capacité à garder "
        "les nombres en tête.",
        "## Symboles  ·  Vitesse de traitement",
        "Repérer le plus vite possible si un symbole figure dans un groupe.",
    ]),
    ("Les dix épreuves  (3 sur 3)", [
        "## Puzzles visuels  ·  Raisonnement perceptif",
        "Choisir les trois pièces qui forment une figure. Évalue la rotation mentale et le raisonnement spatial.",
        "## Information  ·  Compréhension verbale",
        "Des questions de culture générale. Évalue les connaissances acquises à l'école et dans la vie de tous "
        "les jours.",
        "## Code  ·  Vitesse de traitement",
        "Recopier le plus vite possible les symboles associés à des chiffres, à l'aide d'une clé. Évalue la "
        "rapidité et la coordination visuo-motrice.",
    ]),
    ("Les autres versions", [
        "Ce jeu compte dix épreuves principales réparties en quatre domaines. Les vraies évaluations peuvent "
        "aussi comporter des épreuves complémentaires que l'examinateur peut ajouter ou utiliser en remplacement.",
        "Les évaluations sont révisées de temps en temps : les tâches sont mises à jour, les domaines peuvent être "
        "découpés autrement, et les scores sont recalculés sur de nouveaux groupes de personnes. Quelle que soit "
        "la version, la séance elle-même se déroule à peu près de la même façon.",
        "Les enfants passent une version conçue pour leur âge, qui fonctionne de manière très similaire.",
    ]),
]

INDEXES = [
    ("Les quatre domaines", [
        "## Compréhension verbale  (Similitudes, Vocabulaire, Information)",
        "Raisonner avec des mots, et les connaissances acquises par le langage.",
        "## Raisonnement perceptif  (Cubes, Matrices, Puzzles visuels)",
        "Raisonner avec des formes et des motifs : résoudre des problèmes visuels nouveaux, sans mots.",
        "## Mémoire de travail  (Mémoire des chiffres, Arithmétique)",
        "Garder une information en tête quelques secondes tout en l'utilisant.",
        "## Vitesse de traitement  (Symboles, Code)",
        "La rapidité et la précision avec lesquelles vous réalisez des tâches visuelles simples.",
        "Chaque domaine est calculé à partir de ses épreuves, et le résultat global à partir des dix.",
    ]),
]

SCORES = [
    ("Comprendre les scores", [
        "## Comparé aux personnes de votre âge",
        "Les points obtenus à une épreuve sont comparés à ceux d'un grand groupe de personnes de votre âge. Un "
        "score indique où vous vous situez parmi elles, pas combien de réponses étaient justes.",
        "## Épreuves, domaines et ensemble",
        "Chaque épreuve reçoit un score, chacun des quatre domaines en reçoit un à partir de ses épreuves, et un "
        "résultat global les réunit tous. Environ deux personnes sur trois obtiennent un score proche de la "
        "moyenne à chacun d'eux.",
        "## Les centiles",
        "Un centile de 75 signifie que vous avez fait mieux que 75 personnes de votre âge sur 100. Ce n'est pas "
        "un pourcentage de bonnes réponses.",
        "## Des intervalles, pas des points",
        "Tout test comporte une erreur de mesure : les vrais comptes rendus donnent donc un intervalle de "
        "confiance plutôt qu'un seul chiffre. Un petit écart entre deux scores ne veut en général rien dire.",
    ]),
    ("Les scores dans ce jeu", [
        "## Les rangs",
        "Les épreuves, les quatre domaines et l'évaluation complète reçoivent un rang de D à S : D, C, B, A, et "
        "S pour les meilleurs des meilleurs. Le rang de l'évaluation complète est votre Rang global. Les "
        "standards utilisés ont été inventés pour ce jeu : les rangs ne mesurent donc que vos propres progrès. "
        "Vous pouvez les masquer dans les paramètres.",
        "## La cote des puzzles",
        "Les séries classées fonctionnent comme la cote Elo des problèmes d'échecs. Chaque puzzle a un niveau "
        "de difficulté, et votre cote monte quand vous en résolvez un et baisse quand vous en ratez un, "
        "d'autant plus que le résultat est inattendu. Les puzzles sont choisis selon votre cote, si bien "
        "que vous en résoudrez environ la moitié. Cette cote ne vous compare qu'aux puzzles de ce jeu.",
        "## Le défi quotidien",
        "Dix puzzles d'une même épreuve, du plus facile jusqu'au-delà de l'item le plus difficile du vrai test. "
        "Tout le monde reçoit les mêmes puzzles chaque jour. Seule votre première tentative de la journée compte.",
    ]),
]

MYTHS = [
    ("Mythes et réalités", [
        "## « Votre score est fixé pour la vie. »",
        "Les scores des adultes sont assez stables, mais pas gravés dans le marbre. L'éducation, la santé et les "
        "circonstances de la vie jouent un rôle, et les scores peuvent évoluer au fil des années.",
        "## « Les jeux d'entraînement cérébral rendent plus intelligent. »",
        "L'entraînement vous rend meilleur aux tâches que vous pratiquez. De grandes synthèses ont trouvé peu de "
        "preuves que ces progrès se transfèrent à l'intelligence générale. Ce jeu vous rendra meilleur à ces "
        "puzzles. Il ne vous rendra pas plus intelligent.",
        "## « Un test en ligne m'a donné mon vrai score. »",
        "Les vraies évaluations sont étalonnées sur de grands échantillons choisis avec soin et passés dans des "
        "conditions contrôlées. Ce n'est pas le cas des tests en ligne, ce jeu compris : leurs résultats ne "
        "peuvent pas être comparés à de vrais scores.",
    ]),
    ("Mythes et réalités  (suite)", [
        "## « Un score à un test mesure votre valeur. »",
        "Ces tests mesurent un ensemble précis de compétences de raisonnement, de mémoire et de rapidité. "
        "Ils ne disent rien de la gentillesse, de la créativité, de la détermination ni de la plupart des choses "
        "qui font qu'une vie se passe bien.",
        "## « Un grand écart entre mes domaines veut dire que quelque chose ne va pas. »",
        "Des écarts nets entre domaines sont courants dans la population générale. Seul un "
        "professionnel qualifié, qui considère l'ensemble de la situation, peut dire si un profil est significatif.",
        "## « Les scores augmentent de génération en génération. »",
        "C'est en partie vrai. Les scores moyens ont augmenté régulièrement au cours du "
        "XXe siècle (l'effet Flynn). C'est l'une des raisons pour lesquelles les tests sont réétalonnés "
        "régulièrement.",
    ]),
]

ABOUT = [
    ("À propos de Puzzleth", [
        "Puzzleth est un jeu d'entraînement inspiré de la structure et des règles de passation des vraies "
        "évaluations cognitives individuelles. Chaque puzzle est généré par le jeu. Aucun item d'un vrai test "
        "n'est utilisé, et le jeu n'est affilié à aucun éditeur de tests ni approuvé par l'un d'eux.",
        "## Ce n'est pas un test psychologique",
        "Ses rangs reposent sur des standards approximatifs inventés pour ce jeu. Ils ne peuvent pas être "
        "comparés aux résultats d'une vraie évaluation, ne permettent aucun diagnostic et ne doivent pas servir à des décisions "
        "scolaires, professionnelles, juridiques ou médicales.",
        "## À qui s'adresse-t-il ?",
        "Aux personnes inquiètes avant une évaluation qui veulent savoir à quoi s'attendre. À celles qui aiment "
        "les puzzles difficiles. Et à toute personne curieuse de savoir comment fonctionnent ces évaluations.",
    ]),
]

TOPICS = [
    ("expect", "À quoi s'attendre", EXPECT),
    ("subtests", "Les dix épreuves", SUBTESTS),
    ("indexes", "Les quatre domaines", INDEXES),
    ("scores", "Comprendre les scores", SCORES),
    ("myths", "Mythes et réalités", MYTHS),
    ("about", "À propos du jeu", ABOUT),
]
TOPICS = [(key, spacing(title), [(spacing(t), [spacing(p) for p in paras]) for t, paras in pages])
          for key, title, pages in TOPICS]
