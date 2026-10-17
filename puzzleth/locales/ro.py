"""Romanian. The player is addressed with "tu"; Romanian puts "de" between a number from 20 on and its
noun, which plural templates write as {de}."""

ABBREVIATIONS = {
    "BD": "CU", "SI": "AS", "DS": "MC", "MR": "MA", "VC": "VO",
    "AR": "AR", "SS": "CS", "VP": "PV", "IN": "IN", "CD": "CO",
    "VCI": "ICV", "PRI": "IRP", "WMI": "IML", "PSI": "IVP",
}

STRINGS = {
    # ---------------------------------------------------------------- language choice, disclaimer
    "Choose your language": "Alege limba",
    "The game will use this language. You can change it later in Settings.":
        "Jocul va folosi această limbă. O poți schimba oricând din Setări.",
    "You can change it again any time in Settings.": "O poți schimba din nou oricând din Setări.",
    "Language": "Limba",
    "I understand": "Am înțeles",
    "Practising test formats can raise scores on a real test. If you take a clinical assessment, tell the "
    "examiner you have practised.":
        "Exersarea formatelor de test poate crește scorurile la un test real. Dacă faci o evaluare clinică, "
        "spune-i examinatorului că ai exersat.",

    # ---------------------------------------------------------------- menu
    "Begin Full Assessment": "Evaluare completă",
    "Daily": "Zilnic",
    "Daily  {solved}/10": "Zilnic  {solved}/10",
    "Learn": "Învață",
    "Leaderboard": "Clasament",
    "Settings": "Setări",
    "About": "Despre",
    "Quit": "Ieșire",
    "Support Development": "Susține proiectul",
    "Update available": "Actualizare disponibilă",
    "{n} / 10 skills measured  ·  click any node to train it":
        "{n} / 10 abilități evaluate  ·  clic pe una ca s-o antrenezi",
    "{n} / 10 skills measured  ·  tap any node to train it":
        "{n} / 10 abilități evaluate  ·  atinge una ca s-o antrenezi",
    "  ·  daily streak {streak}": "  ·  serie zilnică: {streak}",
    "Turn your phone sideways": "Întoarce telefonul orizontal",
    "Puzzleth is played in landscape": "Puzzleth se joacă în modul peisaj",

    # ---------------------------------------------------------------- skill tree and its tooltips
    "SCORE": "SCOR",
    "scores hidden": "scoruri ascunse",
    "complete all 10": "termină toate 10",
    ("{n} attempt", "{n} attempts"): ("{n} încercare", "{n} {de}încercări"),
    "Measured  ·  scores hidden  ·  {attempts}": "Evaluat  ·  scoruri ascunse  ·  {attempts}",
    "Measured  ·  scores hidden": "Evaluat  ·  scoruri ascunse",
    "  ·  raw {raw} / {max}": "  ·  brut {raw} / {max}",
    "Not yet measured": "Încă neevaluat",
    "Puzzle rating {rating}  ·  peak {peak}": "Rating puzzle-uri {rating}  ·  maxim {peak}",
    "Rated puzzle sets available": "Sunt disponibile seturi cu rating",

    # ---------------------------------------------------------------- subtests, indexes, classifications
    "Block Design": "Cuburi",
    "Similarities": "Asemănări",
    "Digit Span": "Memoria cifrelor",
    "Matrix Reasoning": "Matrice",
    "Vocabulary": "Vocabular",
    "Arithmetic": "Aritmetică",
    "Symbol Search": "Căutare de simboluri",
    "Visual Puzzles": "Puzzle vizual",
    "Information": "Informații",
    "Coding": "Codare",
    "Verbal Comprehension": "Comprehensiune verbală",
    "Perceptual Reasoning": "Raționament perceptiv",
    "Working Memory": "Memorie de lucru",
    "Processing Speed": "Viteză de procesare",

    # ---------------------------------------------------------------- what each subtest measures
    "Visual-spatial analysis and construction": "Analiză și construcție vizual-spațială",
    "Verbal concept formation and abstract reasoning": "Formarea conceptelor verbale și raționament abstract",
    "Auditory working memory, attention and mental manipulation":
        "Memorie de lucru auditivă, atenție și manipulare mentală",
    "Fluid reasoning and abstract pattern detection": "Raționament fluid și detectarea tiparelor abstracte",
    "Word knowledge and verbal concept formation": "Cunoașterea cuvintelor și formarea conceptelor verbale",
    "Mental manipulation, concentration and numerical reasoning":
        "Manipulare mentală, concentrare și raționament numeric",
    "Visual scanning speed and discrimination": "Viteza de explorare vizuală și discriminare",
    "Spatial reasoning and mental rotation": "Raționament spațial și rotație mentală",
    "General knowledge acquired from culture and education": "Cunoștințe generale dobândite din cultură și educație",
    "Processing speed, visual-motor coordination and associative learning":
        "Viteză de procesare, coordonare vizual-motorie și învățare asociativă",

    # ---------------------------------------------------------------- rules of the real test
    "Recreate the model design using blocks with red, white and half-red/half-white faces.":
        "Reproduci modelul folosind cuburi cu fețe roșii, albe și pe jumătate roșii, pe jumătate albe.",
    "Items 1–8 use 4 blocks (2×2); items 9–14 use 9 blocks (3×3).":
        "Itemii 1–8 folosesc 4 cuburi (2×2); itemii 9–14 folosesc 9 cuburi (3×3).",
    "Time limits: 30 s (items 1–4), 60 s (5–8), 120 s (9–14).":
        "Limite de timp: 30 s (itemii 1–4), 60 s (5–8), 120 s (9–14).",
    "Items 1–2: 2 pts. Items 3–8: 4 pts. Items 9–14: 4 pts plus up to 3 speed-bonus points.":
        "Itemii 1–2: 2 p. Itemii 3–8: 4 p. Itemii 9–14: 4 p plus până la 3 puncte bonus pentru viteză.",
    "Later models have no guide lines — you must work out where each block's edges are.":
        "Modelele de mai târziu nu au linii ajutătoare — trebuie să găsești singur marginile cuburilor.",
    "Adults start at item 5; reversal rule applies. Discontinue after 2 consecutive scores of 0.":
        "Adulții încep la itemul 5; se aplică regula revenirii. Oprire după 2 scoruri de 0 la rând.",
    "Two words are read aloud; you explain how they are alike.":
        "Se citesc două cuvinte; explici prin ce se aseamănă.",
    "2 points: the abstract, general category the two belong to.":
        "2 puncte: categoria generală, abstractă, din care fac parte amândouă.",
    "1 point: a concrete, specific property they share.":
        "1 punct: o proprietate concretă, specifică, pe care o au în comun.",
    "0 points: a difference, something only one has, or a vague/wrong answer.":
        "0 puncte: o diferență, ceva propriu doar unuia sau un răspuns vag ori greșit.",
    "Adults start at item 4. If either of the first two isn't perfect, earlier items are given in reverse.":
        "Adulții încep la itemul 4. Dacă unul din primii doi nu e perfect, se dau itemii anteriori, în ordine "
        "inversă.",
    "Discontinue after 3 consecutive scores of 0. No time limit.":
        "Oprire după 3 scoruri de 0 consecutive. Fără limită de timp.",
    "Discontinue after 3 consecutive scores of 0.": "Oprire după 3 scoruri de 0 consecutive.",
    "Three tasks: Forward (same order), Backward (reverse), Sequencing (lowest to highest).":
        "Trei sarcini: Direct (aceeași ordine), Invers (ordine inversă), Ordonare (de la cea mai mică la cea mai "
        "mare).",
    "Digits are presented at a rate of one per second and never repeated.":
        "Cifrele sunt prezentate câte una pe secundă și nu se repetă niciodată.",
    "Each span length has two trials; each correct trial earns 1 point.":
        "Fiecare lungime are două încercări; fiecare încercare corectă valorează 1 punct.",
    "A task stops when both trials of the same length are failed.":
        "O sarcină se oprește când ambele încercări de aceeași lungime sunt greșite.",
    "Each task begins with a sample trial that isn't scored.":
        "Fiecare sarcină începe cu o încercare de probă care nu se punctează.",
    "Look at an incomplete matrix or analogy and pick the option that completes it.":
        "Privești o matrice sau o analogie incompletă și alegi varianta care o completează.",
    "Rules can act along rows, columns, or both: shape, colour, number, size, fill, rotation.":
        "Regulile pot acționa pe rânduri, pe coloane sau pe ambele: formă, culoare, număr, mărime, umplere, "
        "rotație.",
    "There are five response options; exactly one is correct. 1 point each.":
        "Există cinci variante; exact una este corectă. 1 punct pe item.",
    "No strict limit, but examiners prompt after about 30 seconds.":
        "Fără limită strictă, dar examinatorul te grăbește după circa 30 de secunde.",
    "Adults start at item 4; reversal rule applies.": "Adulții încep la itemul 4; se aplică regula revenirii.",
    "You are asked \"What does ___ mean?\" and give a definition.":
        "Ești întrebat „Ce înseamnă ___?” și dai o definiție.",
    "2 points: a precise definition capturing the word's central meaning.":
        "2 puncte: o definiție precisă, care surprinde sensul principal al cuvântului.",
    "1 point: a vague, partial, or overly narrow definition (e.g. one example use).":
        "1 punct: o definiție vagă, parțială sau prea restrânsă (de exemplu, un singur exemplu de folosire).",
    "0 points: a wrong or unrelated meaning.": "0 puncte: un sens greșit sau fără legătură.",
    "Adults start at item 5; reversal rule applies.": "Adulții încep la itemul 5; se aplică regula revenirii.",
    "Word problems are read aloud and solved in your head — no paper or pencil.":
        "Problemele sunt citite cu voce tare și se rezolvă în minte, fără hârtie.",
    "30-second limit per item, timed from the end of the reading.":
        "Limită de 30 de secunde pe item, cronometrată de la sfârșitul citirii.",
    "You may ask for the problem to be repeated once; the timer keeps running.":
        "Poți cere o dată repetarea problemei; cronometrul nu se oprește.",
    "1 point for each correct answer.": "1 punct pentru fiecare răspuns corect.",
    "Adults start at item 6; reversal rule applies.": "Adulții încep la itemul 6; se aplică regula revenirii.",
    "Each row shows two target symbols and a search group of five.":
        "Fiecare rând arată două simboluri-țintă și un grup de căutare de cinci simboluri.",
    "Mark YES if either target appears in the search group, NO if neither does.":
        "Alegi DA dacă oricare dintre ținte apare în grup și NU dacă nu apare niciuna.",
    "Distractors are deliberately similar: mirrored, rotated or one stroke different.":
        "Simbolurile-capcană sunt intenționat asemănătoare: în oglindă, rotite sau cu o linie diferită.",
    "120-second limit. Work in order without skipping.":
        "Limită de 120 de secunde. Lucrezi în ordine, fără să sari peste.",
    "Score = correct answers minus incorrect answers.": "Scor = răspunsuri corecte minus răspunsuri greșite.",
    "Choose the three pieces that, put together, make the puzzle.":
        "Alegi cele trei piese care, puse împreună, formează figura.",
    "Pieces may need to be rotated (turned), but never flipped over.":
        "Piesele pot fi rotite, dar niciodată întoarse pe partea cealaltă.",
    "Exactly three pieces; all three must be correct to earn the 1 point.":
        "Exact trei piese; toate trei trebuie să fie corecte pentru 1 punct.",
    "30-second time limit per item.": "Limită de 30 de secunde pe item.",
    "General-knowledge questions on a wide range of topics.":
        "Întrebări de cultură generală din domenii foarte variate.",
    "Adults start at item 3; reversal rule applies.": "Adulții încep la itemul 3; se aplică regula revenirii.",
    "A key pairs each digit 1–9 with a unique symbol.":
        "O cheie asociază fiecărei cifre de la 1 la 9 un simbol unic.",
    "On the real test you draw the matching symbol under each digit.":
        "În testul real desenezi simbolul potrivit sub fiecare cifră.",
    "120-second limit. Work in order — skipping is not allowed.":
        "Limită de 120 de secunde. Lucrezi în ordine — nu ai voie să sari peste.",
    "Score = number of correct responses (max 135).": "Scor = numărul de răspunsuri corecte (maximum 135).",

    # ---------------------------------------------------------------- how to play here
    "Click or tap a block to turn it to its next face; right-click or the scroll wheel turns it back.":
        "Clic sau atingere pe un cub: fața următoare. Clic dreapta sau rotița: fața anterioară.",
    "The design is checked automatically. Space or the Give up button skips an item.":
        "Modelul se verifică automat. Space sau butonul Renunț sar peste item.",
    "Pick the answer an examiner would score highest.":
        "Alege răspunsul pe care un examinator l-ar puncta cel mai bine.",
    "Click an answer or press 1–4.": "Dă clic pe un răspuns sau apasă 1–4.",
    "Listen to the digits (they are also shown), then type your answer and press Enter.":
        "Ascultă cifrele (sunt și afișate), apoi tastează răspunsul și apasă Enter.",
    "Backspace corrects. The answer submits automatically at full length.":
        "Backspace corectează. Răspunsul se trimite singur când are lungimea completă.",
    "Click an option or press 1–5.": "Dă clic pe o variantă sau apasă 1–5.",
    "Choose the definition that would earn the most credit.":
        "Alege definiția care ar primi cele mai multe puncte.",
    "The problem is shown while it's 'read', then hidden.":
        "Problema este afișată cât timp este „citită”, apoi este ascunsă.",
    "Type your answer and press Enter.  R repeats the problem once.":
        "Tastează răspunsul și apasă Enter.  R repetă problema o dată.",
    "YES:  Y  or  ←        NO:  N  or  →": "DA:  Y  sau  ←        NU:  N  sau  →",
    "Or click the buttons.": "Sau dă clic pe butoane.",
    "Click pieces (or press 1–6) to select three, then press Enter.":
        "Dă clic pe piese (sau apasă 1–6) ca să alegi trei, apoi apasă Enter.",
    "Here the lookup is reversed: each box shows a symbol. Find it in the key and type its digit (1–9), or tap "
    "it in the key. The key is new every session.":
        "Aici e invers: fiecare căsuță arată un simbol. Găsește-l în cheie și tastează-i cifra (1–9) sau "
        "atinge-l. Cheia e nouă la fiecare sesiune.",

    # ---------------------------------------------------------------- subtest briefing
    "Begin": "Începe",
    "Abandon assessment": "Renunță la evaluare",
    "Back": "Înapoi",
    "Rated set": "Set cu rating",
    "Rated set  ·  {rating}": "Set cu rating  ·  {rating}",
    "Rules of the real test": "Regulile testului real",
    "How to play": "Cum se joacă",
    "DAILY CHALLENGE #{n}  ·  SAME PUZZLES FOR EVERYONE TODAY":
        "PROVOCAREA ZILNICĂ #{n}  ·  ACELEAȘI PUZZLE-URI PENTRU TOȚI AZI",
    "FULL ASSESSMENT  ·  SUBTEST {n} OF {total}": "EVALUARE COMPLETĂ  ·  PROBA {n} DIN {total}",
    "RULES OF THE REAL TEST": "REGULILE TESTULUI REAL",
    "HOW TO PLAY HERE": "CUM SE JOACĂ AICI",
    "MODE": "MOD",
    "10 puzzles matched to your rating": "10 puzzle-uri potrivite ratingului tău",
    "You've already played today ({solved}/10). This run is practice and won't change your result.":
        "Ai jucat deja azi ({solved}/10). Runda aceasta e de exercițiu și nu îți schimbă rezultatul.",
    "Daily challenge: 10 puzzles from easy to beyond the real test's hardest item, with feedback after each. "
    "Only your first completed try today counts.":
        "Provocarea zilnică: 10 puzzle-uri, de la ușor la mai greu decât testul real, cu feedback după fiecare. "
        "Contează doar prima încercare încheiată azi.",
    "Test conditions: no feedback, exactly like the real assessment. Your result stays hidden until all ten "
    "subtests are complete.":
        "Condiții de test: fără feedback, exact ca la evaluarea reală. Rezultatul rămâne ascuns până termini "
        "toate cele zece probe.",
    "Training: after every item you'll see the score it earned and the best answer.":
        "Antrenament: după fiecare item vezi ce punctaj a primit și care era cel mai bun răspuns.",
    "Test conditions: no feedback after items. Sample items are still explained.":
        "Condiții de test: fără feedback după itemi. Itemii de probă sunt totuși explicați.",

    # ---------------------------------------------------------------- during a subtest
    "Pause": "Pauză",
    "Pause  (Esc)": "Pauză  (Esc)",
    "DISCONTINUE": "OPRIRE",
    "Stops after {n} consecutive scores of 0": "Se oprește după {n} scoruri de 0 consecutive",
    "Stops after 2 consecutive scores of 0": "Se oprește după 2 scoruri de 0 consecutive",
    "{set}  ·  puzzle {position} of {length}  ·  level {level}":
        "{set}  ·  puzzle-ul {position} din {length}  ·  nivelul {level}",
    "  (beyond the real test)": "  (dincolo de testul real)",
    "Sample item": "Item de probă",
    "Item {item} of {items}": "Itemul {item} din {items}",
    "  ·  reverse order": "  ·  ordine inversă",
    "Rating {rating}  ·  puzzles adapt to your rating":
        "Rating {rating}  ·  puzzle-urile se adaptează ratingului tău",
    "Same puzzles for everyone today  ·  easy to brutal": "Aceleași puzzle-uri pentru toți azi  ·  de la ușor la cumplit",
    "Perfect": "Perfect",
    "Partial credit": "Punctaj parțial",
    "No credit": "Fără puncte",
    "   (sample, not scored)": "   (probă, nepunctată)",
    "Enter to continue": "Enter pentru a continua",
    "Tap to continue": "Atinge pentru a continua",
    "Time limit reached.": "Timpul a expirat.",
    "Correct!": "Corect!",
    "Not quite — ": "Nu chiar — ",
    "check the key and try again.": "verifică cheia și încearcă din nou.",
    "find the symbol in the key above.": "caută simbolul în cheia de mai sus.",
    "a target IS in the group.": "o țintă ESTE în grup.",
    "neither target appears exactly.": "niciuna dintre ținte nu apare exact.",
    "Practice": "Exercițiu",
    "Ready": "Pregătit",
    ("{n} answered", "{n} answered"): ("{n} răspuns", "{n} {de}răspunsuri"),
    ("Practice — {n} correct answer to go. Not timed.", "Practice — {n} correct answers to go. Not timed."):
        ("Exercițiu — mai ai nevoie de {n} răspuns corect. Fără cronometru.",
         "Exercițiu — mai ai nevoie de {n} {de}răspunsuri corecte. Fără cronometru."),
    "{seconds}-second limit  ·  work fast, but accurately": "Limită de {seconds} de secunde  ·  lucrează repede, dar corect",
    "Practice complete": "Exercițiu încheiat",
    "The {seconds}-second timer starts as soon as you continue.":
        "Cronometrul de {seconds} de secunde pornește imediat ce continui.",
    "No feedback is given during the timed section.": "În partea cronometrată nu primești feedback.",
    "Press Space to begin": "Apasă Space ca să începi",
    "Tap to begin": "Atinge ca să începi",
    "your answer": "răspunsul tău",
    "Del": "Șterge",

    # verbal
    ("{n} pt", "{n} pts"): ("{n} punct", "{n} puncte"),
    "correct": "corect",
    "Best answer: {answer}": "Cel mai bun răspuns: {answer}",
    "Abstract category — exactly what earns full credit.":
        "Categorie abstractă — exact ce aduce punctajul maxim.",
    "True, but concrete. 2-point answer: {answer}": "Corect, dar concret. Pentru 2 puncte: {answer}",
    "A 2-point answer: {answer}": "Răspuns de 2 puncte: {answer}",
    "In what way are they alike?": "Prin ce se aseamănă?",
    "Precise definition — full credit.": "Definiție precisă — punctaj maxim.",
    "Vague or partial. Precise: {answer}": "Vagă sau parțială. Precisă: {answer}",
    "Meaning: {answer}": "Sensul: {answer}",
    "What does": "Ce înseamnă cuvântul",
    "mean?": "Alege cea mai bună definiție.",
    "Answer: {answer}": "Răspuns: {answer}",

    # arithmetic
    "Repeat": "Repetă",
    "Repeat  (R)": "Repetă  (R)",
    "Problem hidden — solve it in your head": "Problema e ascunsă — rezolv-o în minte",
    "(tap Repeat to see it once more)": "(atinge Repetă ca s-o mai vezi o dată)",
    "(press R to hear it once more)": "(apasă R ca s-o mai auzi o dată)",
    "(already repeated)": "(deja repetată)",
    "Time limit reached. Answer: {answer}": "Timpul a expirat. Răspuns: {answer}",
    "apples": "mere",
    "pencils": "creioane",
    "stickers": "abțibilduri",
    "books": "cărți",
    "marbles": "bile",
    "cookies": "fursecuri",
    "stamps": "timbre",
    "cards": "cartonașe",
    "passengers": "pasageri",
    "hours": "ore",
    "days": "zile",
    "minutes": "minute",
    "years": "ani",
    "one-half": "jumătate",
    "one-third": "o treime",
    "{name} has {a} {things} and gets {b} more. How many {things} does {name} have now?":
        "{name} are {a} {things} și mai primește {b}. Câte {things} are {name} acum?",
    "{name} had {a} {things} and gave away {b}. How many are left?":
        "{name} avea {a} {things} și a dat {b}. Câte i-au rămas?",
    "There are {a} bags with {b} {things} in each bag. How many {things} are there in all?":
        "Sunt {a} pungi cu câte {b} {things} în fiecare pungă. Câte {things} sunt în total?",
    "Notebooks cost {price} each. How much do {n} notebooks cost?":
        "Un caiet costă {price}. Cât costă {n} caiete?",
    "{name} shares {cookies} equally among {per} friends. How many does each friend get?":
        "{name} împarte {cookies} în mod egal la {per} prieteni. Câte primește fiecare prieten?",
    "A bus has {passengers}. At the next stop, {b} more get on. How many passengers are on the bus?":
        "Într-un autobuz sunt {passengers}. La stația următoare mai urcă {b}. Câți pasageri sunt acum în autobuz?",
    "{name} buys a toy for {cost} and pays with a {pay} bill. How much change does {name} get?":
        "{name} cumpără o jucărie de {cost} și plătește cu o bancnotă de {pay}. Cât rest primește {name}?",
    "{name} buys {n} sandwiches at {price} each and pays with a {pay} bill. How much change does {name} receive?":
        "{name} cumpără {n} sandvișuri a câte {price} bucata și plătește cu o bancnotă de {pay}. Cât rest primește "
        "{name}?",
    "A car travels at {speed}. How far does it travel in {hours}?":
        "O mașină merge cu {speed}. Câți kilometri parcurge în {hours}?",
    "{name} reads {per_day} pages every day. How many pages does {name} read in {days}?":
        "{name} citește {per_day} pagini în fiecare zi. Câte pagini citește {name} în {days}?",
    "{name} has {marbles} and gives {fraction} of them to a friend. How many marbles does {name} have left?":
        "{name} are {marbles} și îi dă unui prieten {fraction} din ele. Câte bile mai are {name}?",
    "A jacket costs {price}. It is on sale for {pct}% off. What is the sale price?":
        "O geacă costă {price}. Are o reducere de {pct}%. Cât costă după reducere?",
    "{workers} workers can paint a house in {hours}. At the same rate, how many hours would it take {new} workers?":
        "{workers} muncitori pot zugrăvi o casă în {hours}. Lucrând la fel de repede, câte ore le-ar trebui unui "
        "număr de {new} muncitori?",
    "{name} scores {a}, {b} and {c} on three tests. What is {name}'s average score?":
        "{name} obține {a}, {b} și {c} puncte la trei teste. Care este punctajul mediu obținut de {name}?",
    "A machine fills {rate} bottles every minute. How many bottles does it fill in {minutes}?":
        "O mașină umple {rate} sticle pe minut. Câte sticle umple în {minutes}?",
    "After a {inc}% price increase, a lamp costs {price}. What did it cost before the increase?":
        "După o scumpire de {inc}%, o lampă costă {price}. Cât costa înainte de scumpire?",
    "{name} and a friend split some money in the ratio {a} to {b}. If {name} gets {share}, how much money was "
    "there in total?":
        "{name} și un prieten își împart niște bani în raportul {a} la {b}. Dacă {name} primește {share}, câți bani "
        "erau în total?",
    "A train travels {distance} at {speed1}, then returns at {speed2}. How many hours does the round trip take?":
        "Un tren parcurge {distance} cu {speed1}, apoi se întoarce cu {speed2}. Câte ore durează drumul dus-întors?",
    "The average of {n} numbers is {avg}. When one number, {drop}, is removed, what is the sum of the remaining "
    "numbers?":
        "Media a {n} numere este {avg}. Dacă se scoate unul dintre ele, {drop}, cât este suma numerelor rămase?",
    "A bike that costs {price} goes up in price by 10%, then the new price is cut by 10%. What does it cost now?":
        "O bicicletă care costă {price} se scumpește cu 10%, apoi noul preț scade cu 10%. Cât costă acum?",
    "One pipe fills a tank in {a}, another in {b}. How many hours do they take working together?":
        "Un robinet umple un bazin în {a}, altul în {b}. În câte ore îl umplu împreună?",
    "{name} is three times as old as a cousin. In {years}, {name} will be twice as old as the cousin. How old is "
    "the cousin now?":
        "{name} are de trei ori vârsta unui văr. Peste {years}, {name} va avea de două ori vârsta vărului. Câți ani "
        "are vărul acum?",
    "Half of a number plus a third of the same number is {sum}. What is the number?":
        "Jumătate dintr-un număr plus o treime din același număr fac {sum}. Care este numărul?",
    "Two cyclists start {distance} apart and ride towards each other at {speed1} and {speed2}. After how many "
    "hours do they meet?":
        "Doi bicicliști pornesc unul spre celălalt de la {distance} distanță, cu {speed1} și {speed2}. După câte ore "
        "se întâlnesc?",

    # digit span
    "Forward": "Direct",
    "Backward": "Invers",
    "Sequencing": "Ordonare",
    "Repeat the digits in the same order.": "Repetă cifrele în aceeași ordine.",
    "Repeat the digits in reverse order.": "Repetă cifrele în ordine inversă.",
    "Repeat the digits in order from lowest to highest.":
        "Repetă cifrele în ordine, de la cea mai mică la cea mai mare.",
    "{task}  ·  sample": "{task}  ·  probă",
    "{task}  ·  {length} digits  ·  trial {trial} of 2": "{task}  ·  {length} cifre  ·  încercarea {trial} din 2",
    "Score {score}": "Scor {score}",
    "Digit Span {task}": "Memoria cifrelor: {task}",
    "e.g.  {example}": "ex.:  {example}",
    "Press Space when ready": "Apasă Space când ești gata",
    "Tap anywhere when ready": "Atinge oriunde când ești gata",
    "Listen…": "Ascultă…",
    "Correct": "Corect",
    "Incorrect": "Greșit",
    "  (sample — not scored)": "  (probă — nepunctată)",
    "Presented: {shown}     Answer: {answer}": "Prezentate: {shown}     Răspuns: {answer}",
    "Each task stops when both trials of one length are failed":
        "Fiecare sarcină se oprește când ambele încercări de o anumită lungime sunt greșite",

    # block design
    "Give up": "Renunț",
    "Give up  (Space)": "Renunț  (Space)",
    "Item abandoned.": "Item abandonat.",
    "Completed in {seconds} s — speed bonus +{bonus}": "Terminat în {seconds} s — bonus de viteză +{bonus}",
    "Completed in {seconds} s": "Terminat în {seconds} s",
    "MODEL": "MODEL",
    "YOUR BLOCKS": "CUBURILE TALE",
    "The model is on the left — compare edge by edge.": "Modelul e în stânga — compară margine cu margine.",

    # matrix reasoning, visual puzzles, speed
    "The answer was option {option}.": "Răspunsul era varianta {option}.",
    "Confirm": "Confirmă",
    "Confirm  (Enter)": "Confirmă  (Enter)",
    "Correct pieces: {pieces}": "Piesele corecte: {pieces}",
    "Time limit reached. Correct pieces: {pieces}": "Timpul a expirat. Piesele corecte: {pieces}",
    "PUZZLE": "FIGURA",
    ("Select {n} more piece", "Select {n} more pieces"): ("Mai alege {n} piesă", "Mai alege {n} piese"),
    "YES": "DA",
    "NO": "NU",
    "TARGETS": "ȚINTE",
    "SEARCH GROUP": "GRUP DE CĂUTARE",
    "KEY": "CHEIE",

    # ---------------------------------------------------------------- results
    "Train again": "Antrenează din nou",
    "Skill tree": "Acasă",
    "NEW PERSONAL BEST": "RECORD PERSONAL NOU",
    "Done": "Gata",
    "SUBTEST COMPLETE": "PROBĂ ÎNCHEIATĂ",
    "Scores are hidden. You can show them in Settings.": "Scorurile sunt ascunse. Le poți afișa din Setări.",
    "Forward {forward}  ·  Backward {backward}  ·  Sequencing {sequencing}":
        "Direct {forward}  ·  Invers {backward}  ·  Ordonare {sequencing}",
    "{correct} correct  ·  {wrong} incorrect  ·  {attempted} attempted":
        "{correct} corecte  ·  {wrong} greșite  ·  {attempted} încercate",
    ("Stopped after {n} item. Every subtest ends after a run of misses, so everyone reaches that point.",
     "Stopped after {n} items. Every subtest ends after a run of misses, so everyone reaches that point."):
        ("Oprit după {n} item. Fiecare probă se încheie după o serie de greșeli, așa că toată lumea ajunge acolo.",
         "Oprit după {n} {de}itemi. Fiecare probă se încheie după o serie de greșeli, așa că toată lumea ajunge "
         "acolo."),
    ("{n} item given, right to the end of the subtest", "{n} items given, right to the end of the subtest"):
        ("{n} item dat, până la capătul probei", "{n} {de}itemi dați, până la capătul probei"),
    "ASSESSMENT COMPLETE": "EVALUARE ÎNCHEIATĂ",
    "Your skill constellation": "Constelația abilităților tale",
    "ALL TEN SUBTESTS DONE": "TOATE CELE ZECE PROBE ÎNCHEIATE",
    "You finished a full assessment under real test conditions: no feedback, real time limits, real stopping "
    "rules. That's the whole experience.":
        "Ai terminat o evaluare completă în condiții reale de test: fără feedback, cu limite de timp și reguli de "
        "oprire reale. Asta e toată experiența.",
    "Scores are hidden. Your results are saved, and you can show them any time in Settings.":
        "Scorurile sunt ascunse. Rezultatele tale sunt salvate și le poți afișa oricând din Setări.",
    "tap to skip": "atinge ca să sari peste",
    "click to skip": "dă clic ca să sari peste",
    "Paused": "Pauză",
    "Timers are stopped (the real test can't be paused!)  ·  F11 toggles fullscreen":
        "Cronometrele sunt oprite (testul real nu poate fi pus pe pauză!)  ·  F11 comută ecranul complet",
    "Resume": "Continuă",
    "Restart subtest": "Reia proba",
    "Quit to skill tree": "Ieși la ecranul principal",
    "Another set": "Alt set",
    "Copy result": "Copiază rezultatul",
    "Copied! Paste it anywhere to share.": "Copiat! Lipește-l oriunde vrei să-l distribui.",
    "Couldn't reach the clipboard.": "Nu s-a putut accesa clipboardul.",
    "Daily #{n}": "Zilnic #{n}",
    "Puzzleth Daily #{n} · {subtest}": "Puzzleth Zilnic #{n} · {subtest}",
    "PUZZLE RATING": "RATING PUZZLE-URI",
    "{solved} of {length} solved": "{solved} din {length} rezolvate",
    ("{n} puzzle played", "{n} puzzles played"): ("{n} puzzle jucat", "{n} {de}puzzle-uri jucate"),
    "  ·  peak {peak}": "  ·  maxim {peak}",
    "  ·  #{rank} of {total} online": "  ·  locul {rank} din {total} online",
    "SOLVED": "REZOLVATE",
    ("Daily streak: {n} day", "Daily streak: {n} days"): ("Serie zilnică: {n} zi", "Serie zilnică: {n} {de}zile"),
    "Practice replay  ·  today's result was {solved}/10": "Rundă de exercițiu  ·  rezultatul de azi a fost {solved}/10",
    "difficulty level of each puzzle": "nivelul de dificultate al fiecărui puzzle",

    # ---------------------------------------------------------------- players and names
    "Restore a player": "Adu un jucător",
    "Cancel": "Anulează",
    "A new player starts with fresh progress and their own settings.":
        "Un jucător nou pornește de la zero, cu propriile setări.",
    "Your progress so far will be kept under this name.": "Progresul de până acum va fi păstrat sub acest nume.",
    "Your progress is saved under this name. Everyone else can add their own.":
        "Progresul tău se salvează sub acest nume. Ceilalți își pot adăuga propriul nume.",
    "Tap the letters, then OK": "Atinge literele, apoi OK",
    "Type your name, or pick each letter with Up/Down and lock it in with Right":
        "Scrie-ți numele sau alege fiecare literă cu Sus/Jos și fixeaz-o cu Dreapta",
    "ENTER YOUR NAME": "SCRIE-ȚI NUMELE",
    "Enter at least one letter": "Scrie cel puțin o literă",
    "{name} is already a player here": "{name} este deja jucător aici",
    "There can be at most {n} players": "Pot exista cel mult {n} jucători",
    "There's already a player called {name} here. Remove them first.":
        "Există deja aici un jucător numit {name}. Elimină-l mai întâi.",
    "Enter all {n} characters of the code": "Introdu toate cele {n} caractere ale codului",
    "Enter the recovery code from Leaderboard > Move to another device on your other device.":
        "Introdu codul de recuperare din Clasament > Mută pe alt dispozitiv de pe celălalt dispozitiv.",
    "Restoring…": "Se restaurează…",
    "Tap the characters, then OK": "Atinge caracterele, apoi OK",
    "Type or paste the code, then press Enter": "Scrie sau lipește codul, apoi apasă Enter",
    "RESTORE A PLAYER": "ADU UN JUCĂTOR",
    "Not played yet": "Încă nu a jucat",
    "Last played today": "A jucat ultima dată azi",
    "Last played yesterday": "A jucat ultima dată ieri",
    ("Last played {n} day ago", "Last played {n} days ago"):
        ("A jucat ultima dată acum {n} zi", "A jucat ultima dată acum {n} {de}zile"),
    "New player": "Jucător nou",
    "Remove…": "Elimină…",
    "Done removing": "Gata cu eliminarea",
    "Restore…": "Adu…",
    "WHO'S PLAYING?": "CINE JOACĂ?",
    "Tap a player twice to remove them and all their progress.":
        "Atinge de două ori un jucător ca să-l elimini, împreună cu tot progresul lui.",
    "Choose your name. Each player keeps their own progress and settings.":
        "Alege-ți numele. Fiecare jucător își păstrează propriul progres și propriile setări.",
    "Tap again to remove": "Atinge din nou ca să elimini",
    "all of this player's progress": "tot progresul acestui jucător",
    "{n} / 10 skills measured": "{n} / 10 abilități evaluate",
    "Playing now": "Joacă acum",

    # ---------------------------------------------------------------- leaderboard and moving devices
    "Play a rated set": "Joacă un set cu rating",
    "Move to another device": "Mută pe alt dispozitiv",
    "Tap again to leave": "Atinge din nou ca să ieși",
    "Leave the leaderboard": "Ieși din clasament",
    "Privacy": "Confidențialitate",
    "Joining…": "Te alături…",
    "Join as {name}": "Alătură-te ca {name}",
    "LEADERBOARD": "CLASAMENT",
    "Puzzle ratings from rated sets, from players everywhere. You're ranked after your first set.":
        "Ratingurile din seturile cu rating ale jucătorilor de pretutindeni. Apari în clasament după primul set.",
    "PLAYER": "JUCĂTOR",
    "RATING": "RATING",
    "PUZZLES": "PUZZLE-URI",
    "Loading…": "Se încarcă…",
    "Nobody is ranked yet. Play a rated set to be the first!":
        "Încă nu e nimeni în clasament. Joacă un set cu rating ca să fii primul!",
    "COMPETE ONLINE": "CONCUREAZĂ ONLINE",
    "Put {name}'s puzzle ratings on the leaderboard.": "Pune ratingurile lui {name} în clasament.",
    "Your name, ratings and progress are sent. The progress is a backup that lets you move to another device "
    "with a recovery code. Leave any time to delete it all from the server.":
        "Se trimit numele, ratingurile și progresul tău. Progresul este o copie de rezervă care îți permite să "
        "te muți pe alt dispozitiv cu un cod de recuperare. Ieși oricând ca să ștergi totul de pe server.",
    "YOU": "TU",
    "of {total} ranked in {subtest}": "din {total} în clasamentul la {subtest}",
    "Unranked": "Neclasat",
    ("{n} more puzzle to be ranked", "{n} more puzzles to be ranked"):
        ("Încă {n} puzzle până intri în clasament", "Încă {n} {de}puzzle-uri până intri în clasament"),
    "Your rating is on its way": "Ratingul tău e pe drum",
    "Unrated": "Fără rating",
    "Play a {subtest} rated set to get a rating": "Joacă un set cu rating la {subtest} ca să primești un rating",
    "Rating {rating}  ·  peak {peak}": "Rating {rating}  ·  maxim {peak}",
    "Copy": "Copiază",
    "New code": "Cod nou",
    "Tap again": "Atinge din nou",
    "Copied!": "Copiat!",
    "Couldn't reach the clipboard. Write the code down instead.":
        "Nu s-a putut accesa clipboardul. Notează codul de mână.",
    "MOVE TO ANOTHER DEVICE": "MUTĂ PE ALT DISPOZITIV",
    "{name}'S RECOVERY CODE": "CODUL DE RECUPERARE AL LUI {name}",
    "Getting your code…": "Se obține codul…",
    "No code yet": "Încă nu există un cod",
    "Your current code will stop working.": "Codul tău actual nu va mai funcționa.",
    "On your other device, choose Restore a player when it asks for a name (or on the Who's playing screen) "
    "and enter this code.":
        "Pe celălalt dispozitiv, alege Adu un jucător când ți se cere un nume (sau din ecranul Cine "
        "joacă?) și introdu acest cod.",
    "{name}'s progress, settings and leaderboard place move there. This device keeps its copy of the progress "
    "but stops posting to the leaderboard.":
        "Progresul, setările și locul lui {name} în clasament se mută acolo. Acest dispozitiv își păstrează "
        "copia progresului, dar nu mai trimite rezultate în clasament.",
    "Keep the code private: anyone who has it can take over this player. If someone else has seen it, get a new "
    "code.":
        "Păstrează codul doar pentru tine: oricine îl are poate prelua acest jucător. Dacă l-a văzut altcineva, "
        "cere un cod nou.",
    "Couldn't reach the leaderboard. Check your connection and try again.":
        "Clasamentul nu poate fi accesat. Verifică conexiunea și încearcă din nou.",
    "Too many wrong codes from here today. Try again tomorrow.":
        "Prea multe coduri greșite de aici azi. Încearcă din nou mâine.",
    "Too many new players from here today. Try again tomorrow.":
        "Prea mulți jucători noi de aici azi. Încearcă din nou mâine.",
    "The leaderboard said no ({error}).": "Clasamentul a refuzat cererea ({error}).",
    "The leaderboard's address, {address}, isn't a web address (see server/README.md).":
        "Adresa clasamentului, {address}, nu este o adresă web (vezi server/README.md).",
    "No player has that code. Check it and try again.":
        "Niciun jucător nu are acest cod. Verifică-l și încearcă din nou.",

    # ---------------------------------------------------------------- learn
    "Start the assessment": "Începe evaluarea",
    "Next": "Următor",
    "Previous": "Anterior",
    "Next topic": "Subiectul următor",
    "Skip": "Sari peste",
    "BEFORE YOUR FIRST FULL ASSESSMENT": "ÎNAINTEA PRIMEI EVALUĂRI COMPLETE",
    "A quick look at what a real session is like. Skip whenever you like.":
        "O privire rapidă asupra unei ședințe reale. Poți sări peste oricând.",
    "LEARN": "ÎNVAȚĂ",

    # ---------------------------------------------------------------- settings
    "SETTINGS": "SETĂRI",
    "Feedback while training": "Feedback la antrenament",
    "After each item, show how it was scored and the best answer. The full assessment never gives feedback, "
    "just like the real test.":
        "După fiecare item, arată cum a fost punctat și care era cel mai bun răspuns. Evaluarea completă nu dă "
        "niciodată feedback, exact ca testul real.",
    "Sound effects": "Efecte sonore",
    "Clicks, timer ticks and the spoken digits in Digit Span. Right/wrong chimes only play when feedback is "
    "shown.":
        "Clicuri, ticăitul cronometrului și cifrele rostite la Memoria cifrelor. Sunetele pentru corect/greșit "
        "se aud doar când feedbackul e activat.",
    "No audio device was found.": "Nu a fost găsit niciun dispozitiv audio.",
    "Music": "Muzică",
    ("Plays the {n} track in your music folder on a shuffled loop. It turns down while digits are read out.",
     "Plays the {n} tracks in your music folder on a shuffled loop. It turns down while digits are read out."):
        ("Redă în buclă, amestecat, piesa din dosarul tău de muzică. Volumul scade cât timp sunt citite cifrele.",
         "Redă în buclă, amestecat, cele {n} {de}piese din dosarul tău de muzică. Volumul scade cât timp sunt "
         "citite cifrele."),
    "Put your own mp3, ogg or wav files in the puzzleth/music folder. None found yet.":
        "Pune propriile fișiere mp3, ogg sau wav în dosarul puzzleth/music. Deocamdată nu există niciunul.",
    "Put your own mp3, ogg or wav files in the puzzleth/music folder or ~/.puzzleth/music. None found yet.":
        "Pune propriile fișiere mp3, ogg sau wav în dosarul puzzleth/music sau ~/.puzzleth/music. Deocamdată "
        "nu există niciunul.",
    "Fullscreen  (F11)": "Ecran complet  (F11)",
    "Use your browser's menu to go fullscreen, or add Puzzleth to your home screen.":
        "Folosește meniul browserului pentru ecran complet sau adaugă Puzzleth pe ecranul de pornire.",
    "Fill the whole screen. In a window, the game scales to any size you like.":
        "Ocupă tot ecranul. Într-o fereastră, jocul se adaptează la orice dimensiune.",
    "On": "Activat",
    "Off": "Dezactivat",
    "Shown": "Afișate",
    "Hidden": "Ascunse",
    # ---------------------------------------------------------------- grade scores (v0.0.3)
    "This is not a psychological test": "Acesta nu este un test psihologic",
    "Puzzleth is a training game modelled on the structure and rules of real one-to-one cognitive assessments. It uses none of their items and is not affiliated with or endorsed by any test publisher.":
        "Puzzleth este un joc de antrenament inspirat de structura și regulile evaluărilor cognitive individuale reale. Nu folosește niciun item al acestora și nu este afiliat cu niciun editor de teste și nici susținut de vreunul.",
    "Its grades come from rough standards made up for this game, not from a standardised sample of people. They cannot be compared with the results of a real assessment.":
        "Calificativele sale provin din standarde aproximative create pentru acest joc, nu dintr-un eșantion standardizat de oameni. Nu pot fi comparate cu rezultatele unei evaluări reale.",
    "It cannot diagnose anything and must not be used for school, work, legal or medical decisions. Only a standardised assessment given by a qualified psychologist can do that.":
        "Nu poate stabili niciun diagnostic și nu trebuie folosit pentru decizii școlare, profesionale, juridice sau medicale. Doar o evaluare standardizată, făcută de un psiholog calificat, poate face asta.",
    "Cognitive puzzle training": "Antrenament cognitiv prin puzzle-uri",
    "Not a psychological test. Grades are training estimates, not clinical results.":
        "Nu este un test psihologic. Calificativele sunt estimări de antrenament, nu rezultate clinice.",
    "NOT A PSYCHOLOGICAL TEST": "NU ESTE UN TEST PSIHOLOGIC",
    "Grades use rough standards made up for this game. They show trends in your training, nothing more.":
        "Calificativele folosesc standarde create pentru acest joc. Arată doar evoluția antrenamentului tău.",
    "How assessments work, what a session is like, and how to read the scores":
        "Cum funcționează evaluările, cum decurge o ședință și cum se citesc scorurile",
    "Grades": "Calificative",
    "Show the D to S grades of subtests, areas and the overall Grade Score. Hide them to practise without a grade. Puzzle ratings and daily results still show.":
        "Arată calificativele de la D la S ale probelor, ale domeniilor și Calificativul general. Ascunde-le ca să exersezi fără calificativ. Ratingurile puzzle-urilor și rezultatele zilnice rămân afișate.",
    "Grade Score": "Calificativ general",
    "GRADE SCORE": "CALIFICATIV GENERAL",
    "GRADE": "CALIFICATIV",
    "Grade {grade}  ·  {label}": "Calificativ {grade}  ·  {label}",
    "Personal best {grade}  ·  {attempts}": "Record personal {grade}  ·  {attempts}",
    ("{n} skill point of 19", "{n} skill points of 19"):
        ("{n} punct de abilitate din 19", "{n} {de}puncte de abilitate din 19"),
    "Raw {raw} / {max}": "Brut {raw} / {max}",
    "Complete all of its subtests to grade it": "Termină toate probele lui ca să primească un calificativ",
    "Combines all ten subtests": "Combină toate cele zece probe",
    "Take the full assessment to grade it": "Fă evaluarea completă ca să primească un calificativ",
    "Grades run from D up to S": "Calificativele merg de la D la S",
    "A training estimate, not a clinical result": "O estimare de antrenament, nu un rezultat clinic",
    "Outstanding": "Excepțional",
    "Excellent": "Excelent",
    "Solid": "Solid",
    "Developing": "În progres",
    "Just getting started": "Abia la început",
}
