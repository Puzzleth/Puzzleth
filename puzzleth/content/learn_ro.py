"""The Learn screen in Romanian: learn.py translated, with the same topics and pages."""

EXPECT = [
    ("Înainte de ședință", [
        "O evaluare WAIS este o ședință individuală cu un psiholog sau cu un examinator instruit. Cele zece probe "
        "de bază durează de obicei între o oră și o oră și jumătate, uneori ca parte a unei evaluări mai lungi.",
        "Nu ai nimic de învățat și nimic de adus, în afară de ochelari sau proteză auditivă, dacă le folosești. "
        "Somnul, mâncarea și medicamentele pe care le iei de obicei contează mai mult decât orice pregătire.",
        "Este normal să fii emoționat. Examinatorii văd zilnic oameni emoționați, iar primii itemi din fiecare "
        "probă sunt ușori intenționat, în parte ca să te ajute să te acomodezi.",
        "Poți pune întrebări înainte de a începe și poți cere o scurtă pauză între probe.",
    ]),
    ("Ce face examinatorul", [
        "## Citește după un text fix",
        "Instrucțiunile sunt citite cuvânt cu cuvânt, ca toată lumea să primească exact același test. De aceea "
        "pot suna oficial.",
        "## Nu îți spune dacă ai răspuns corect",
        "Asta îi neliniștește cel mai mult pe oameni. O expresie neutră sau un simplu „bine” după fiecare "
        "răspuns este regula pentru toți cei evaluați. Nu este un semn că ai greșit.",
        "## Te cronometrează și notează",
        "La probele cronometrate se folosește la vedere un cronometru, iar răspunsurile date oral sunt notate "
        "cuvânt cu cuvânt. Și asta este o procedură normală.",
        "## Te poate întreba „Poți să-mi spui mai mult?”",
        "La probele verbale, după un răspuns vag urmează o întrebare neutră. Înseamnă că răspunsul ar putea "
        "primi mai multe puncte dacă explici mai pe larg, nu că ar fi greșit.",
    ]),
    ("Reguli pe care le poți observa", [
        "## Începutul de la mijloc",
        "Adulții încep de obicei cu câțiva itemi mai încolo, nu de la itemul 1. Examinatorul știe deja de unde.",
        "## Întoarcerea înapoi",
        "Dacă unul dintre primele două răspunsuri nu este complet corect, examinatorul se întoarce la itemi mai "
        "ușori. Aceasta este regula revenirii. Ea găsește un punct de plecare sigur, iar apoi primești punctaj "
        "pentru fiecare item mai ușor pe care l-ai sărit.",
        "## Oprirea după câteva greșeli",
        "Fiecare probă se încheie după un anumit număr de răspunsuri greșite la rând (două sau trei, în funcție "
        "de probă). Toată lumea ajunge acolo, pentru că itemii devin tot mai grei, până când sunt grei pentru "
        "aproape oricine. Oprirea face parte din test, nu este un eșec.",
        "## Poți spune „Nu știu”",
        "Ai voie să ghicești și ai voie să treci peste. Nu se așteaptă să răspunzi la tot.",
    ]),
    ("După aceea", [
        "Răspunsurile tale sunt transformate în scoruri standard pentru fiecare probă (de la 1 la 19, media 10), "
        "apoi în patru scoruri de indice și un IQ total (media 100).",
        "Un raport bun dă intervale, nu doar numere izolate, și pune scorurile în contextul istoricului tău, al "
        "educației și al motivului pentru care ai fost evaluat. Cifrele sunt o piesă dintr-un tablou mai mare.",
        "Rezultatele inegale sunt normale. Majoritatea oamenilor au scoruri vizibil mai mari în unele domenii "
        "decât în altele.",
        "Dacă te-ai antrenat cu acest joc sau cu ceva asemănător, spune-i examinatorului. Exersarea poate crește "
        "puțin scorurile, iar examinatorul poate ține cont de asta.",
    ]),
]

SUBTESTS = [
    ("Cele zece probe  (1 din 3)", [
        "## Cuburi  ·  Raționament perceptiv",
        "Copierea unui model roșu cu alb folosind cuburi. Urmărește capacitatea de a descompune o imagine în părți "
        "și de a o reconstrui, sub presiunea timpului.",
        "## Asemănări  ·  Comprehensiune verbală",
        "„Prin ce se aseamănă un pian și o chitară?” Urmărește raționamentul verbal abstract: găsirea categoriei, "
        "nu a unui detaliu de suprafață.",
        "## Memoria cifrelor  ·  Memorie de lucru",
        "Repetarea unor cifre în aceeași ordine, invers și în ordine crescătoare. Urmărește capacitatea de a ține "
        "informația în minte și de a lucra cu ea.",
        "## Matrice  ·  Raționament perceptiv",
        "Găsirea piesei care lipsește dintr-un model. Un test clasic de raționament fluid, adică rezolvarea unor "
        "probleme noi fără a te baza pe cunoștințe.",
    ]),
    ("Cele zece probe  (2 din 3)", [
        "## Vocabular  ·  Comprehensiune verbală",
        "Explicarea sensului unor cuvinte. Cunoașterea cuvintelor este unul dintre cei mai buni predictori ai "
        "scorului total.",
        "## Aritmetică  ·  Memorie de lucru",
        "Probleme rezolvate în minte. Contează mai puțin priceperea la matematică și mai mult capacitatea de a "
        "ține numerele în minte.",
        "## Căutare de simboluri  ·  Viteză de procesare",
        "Identificarea cât mai rapidă a unui simbol într-un grup.",
    ]),
    ("Cele zece probe  (3 din 3)", [
        "## Puzzle vizual  ·  Raționament perceptiv",
        "Alegerea celor trei piese care formează o figură. Urmărește rotația mentală și raționamentul spațial.",
        "## Informații  ·  Comprehensiune verbală",
        "Întrebări de cultură generală. Urmărește cunoștințele dobândite la școală și din viața de zi cu zi.",
        "## Codare  ·  Viteză de procesare",
        "Copierea cât mai rapidă a simbolurilor care corespund unor cifre, după o cheie. Urmărește viteza și "
        "coordonarea vizual-motorie.",
    ]),
    ("Ediții", [
        "Acest joc urmează WAIS-IV (2008): zece probe de bază care dau patru scoruri de indice. WAIS-IV are și "
        "cinci probe suplimentare, pe care examinatorul le poate adăuga sau folosi ca înlocuitori.",
        "O ediție mai nouă, WAIS-5, a apărut în 2024. Ea împarte Raționamentul perceptiv în Vizual-spațial și "
        "Raționament fluid și calculează IQ-ul total din mai puține probe. Multe cabinete folosesc încă WAIS-IV, "
        "iar ședința în sine se desfășoară cam la fel.",
        "Copiii sunt evaluați cu un alt test, WISC, care funcționează foarte asemănător.",
    ]),
]

INDEXES = [
    ("Cele patru scoruri de indice", [
        "## Comprehensiune verbală  (Asemănări, Vocabular, Informații)",
        "Raționamentul cu ajutorul cuvintelor și cunoștințele acumulate prin limbaj.",
        "## Raționament perceptiv  (Cuburi, Matrice, Puzzle vizual)",
        "Raționamentul cu forme și modele: rezolvarea unor probleme vizuale noi, fără cuvinte.",
        "## Memorie de lucru  (Memoria cifrelor, Aritmetică)",
        "Păstrarea informației în minte câteva secunde, în timp ce faci ceva cu ea.",
        "## Viteză de procesare  (Căutare de simboluri, Codare)",
        "Cât de repede și de corect poți îndeplini sarcini vizuale simple.",
        "Fiecare indice se calculează din probele sale, iar IQ-ul total din toate cele zece.",
    ]),
]

SCORES = [
    ("Cum funcționează scorurile", [
        "## De la scorul brut la scorul standard",
        "Punctele obținute la o probă sunt comparate cu cele ale persoanelor de vârsta ta și transformate într-un "
        "scor standard de la 1 la 19. 10 este media, iar cam doi din trei oameni obțin între 7 și 13.",
        "## Scorurile de indice și IQ-ul total",
        "Acestea folosesc altă scală: 100 este media, iar fiecare 15 puncte înseamnă o abatere standard. Cam doi "
        "din trei oameni obțin între 85 și 115, iar cam 2 din 100 obțin peste 130.",
        "## Percentilele",
        "Percentila 75 înseamnă că ai obținut un scor mai mare decât 75 din 100 de persoane de vârsta ta. Nu este "
        "procentul de răspunsuri corecte.",
        "## Intervale, nu puncte fixe",
        "Orice test are o eroare de măsurare, așa că rapoartele reale dau un interval de încredere, de exemplu "
        "între 102 și 112. Câteva puncte de diferență între două scoruri nu înseamnă de obicei nimic.",
    ]),
    ("Scorurile din acest joc", [
        "## Scoruri de test",
        "Evaluarea completă și probele în stil WAIS afișează scoruri standard, scoruri de indice și un scor total "
        "(înlocuitorul jocului pentru IQ-ul total), ca să vezi cum este alcătuit un raport real. Normele din "
        "spatele lor sunt create pentru acest joc, așa că cifrele îți arată doar propriul progres. Le poți ascunde "
        "din Setări.",
        "## Ratingul puzzle-urilor",
        "Seturile cu rating funcționează ca ratingul pentru problemele de șah. Fiecare puzzle are un nivel de "
        "dificultate, iar ratingul tău crește când rezolvi unul și scade când greșești, cu atât mai mult cu cât "
        "rezultatul e mai neașteptat. Puzzle-urile sunt alese pe măsura ratingului tău, așa că vei rezolva cam "
        "jumătate dintre ele. Ratingul te compară doar cu puzzle-urile din acest joc.",
        "## Provocarea zilnică",
        "Zece puzzle-uri dintr-o singură probă, de la ușor până dincolo de cel mai greu item al testului real. "
        "Toată lumea primește aceleași puzzle-uri în fiecare zi. Contează doar prima ta încercare din ziua "
        "respectivă.",
    ]),
]

MYTHS = [
    ("Mituri și adevăruri", [
        "## „IQ-ul rămâne același toată viața.”",
        "Scorurile adulților sunt destul de stabile, dar nu bătute în cuie. Educația, sănătatea și împrejurările "
        "vieții contează, iar scorurile se pot schimba de-a lungul anilor.",
        "## „Antrenamentul cerebral îți crește IQ-ul.”",
        "Exersarea te face mai bun la sarcinile pe care le exersezi. Analize ample au găsit puține dovezi că "
        "progresul se transferă asupra inteligenței generale. Acest joc te va face mai bun la aceste puzzle-uri. "
        "Nu te va face mai inteligent.",
        "## „Un test IQ online mi-a spus ce IQ am.”",
        "Testele IQ reale sunt standardizate pe eșantioane mari, alese cu grijă, și se aplică în condiții "
        "controlate. Testele online, inclusiv acest joc, nu sunt, așa că cifrele lor nu pot fi comparate cu "
        "scorurile reale.",
    ]),
    ("Mituri și adevăruri  (continuare)", [
        "## „IQ-ul arată cât valorezi.”",
        "Testele IQ măsoară un set anume de abilități de raționament, memorie și viteză. Nu spun nimic despre "
        "bunătate, creativitate, perseverență sau despre cea mai mare parte din ceea ce face ca o viață să "
        "meargă bine.",
        "## „O diferență mare între scorurile mele de indice înseamnă că ceva nu e în regulă.”",
        "Diferențele de 10 puncte sau mai mult între scorurile de indice sunt frecvente în populația generală. "
        "Doar un specialist calificat, privind întregul tablou, poate spune dacă un anumit profil contează.",
        "## „Scorurile cresc de la o generație la alta.”",
        "Parțial adevărat. Scorurile medii au crescut cu aproximativ 3 puncte pe deceniu în secolul XX (efectul "
        "Flynn). Acesta este unul dintre motivele pentru care testele sunt renormate din când în când.",
    ]),
]

ABOUT = [
    ("Despre Puzzleth", [
        "Puzzleth este un joc de antrenament gratuit și open-source, inspirat de structura și regulile de "
        "administrare ale WAIS-IV. Fiecare puzzle este generat de joc. Niciunul dintre itemii testului real nu "
        "este folosit, iar jocul nu este afiliat cu editorul testului și nici susținut de acesta.",
        "## Acesta nu este un test IQ real",
        "Scorurile sale provin din norme aproximative create pentru acest joc. Nu pot fi comparate cu un IQ real, "
        "nu pot stabili niciun diagnostic și nu trebuie folosite pentru decizii școlare, profesionale, juridice "
        "sau medicale.",
        "## Pentru cine este",
        "Pentru cei care au emoții înaintea unei evaluări și vor să știe cum decurge. Pentru cei cărora le plac "
        "puzzle-urile grele. Și pentru oricine e curios cum funcționează testele de inteligență.",
    ]),
]

TOPICS = [
    ("expect", "La ce să te aștepți", EXPECT),
    ("subtests", "Cele zece probe", SUBTESTS),
    ("indexes", "Cei patru indici", INDEXES),
    ("scores", "Cum se citesc scorurile", SCORES),
    ("myths", "Mituri despre IQ", MYTHS),
    ("about", "Despre joc", ABOUT),
]
