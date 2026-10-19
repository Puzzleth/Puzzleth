"""The Learn screen in Romanian: learn.py translated, with the same topics and pages."""

EXPECT = [
    ("Înainte de ședință", [
        "O evaluare cognitivă este o ședință individuală cu un psiholog sau cu un examinator instruit. Probele "
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
        "Răspunsurile tale sunt comparate cu cele ale unui grup mare de persoane de vârsta ta și transformate în "
        "scoruri pentru fiecare probă, pentru fiecare dintre cele patru domenii și pe ansamblu.",
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
    ("Alte versiuni", [
        "Acest joc are zece probe de bază, grupate în patru domenii. Evaluările reale pot avea și probe "
        "suplimentare, pe care examinatorul le poate adăuga sau folosi ca înlocuitori.",
        "Evaluările sunt revizuite din când în când: sarcinile sunt actualizate, domeniile pot fi împărțite altfel, "
        "iar scorurile sunt calculate din nou pe grupuri noi de oameni. Indiferent de versiune, ședința în sine se "
        "desfășoară cam la fel.",
        "Copiii sunt evaluați cu o versiune făcută pentru vârsta lor, care funcționează foarte asemănător.",
    ]),
]

INDEXES = [
    ("Cele patru domenii", [
        "## Comprehensiune verbală  (Asemănări, Vocabular, Informații)",
        "Raționamentul cu ajutorul cuvintelor și cunoștințele acumulate prin limbaj.",
        "## Raționament perceptiv  (Cuburi, Matrice, Puzzle vizual)",
        "Raționamentul cu forme și modele: rezolvarea unor probleme vizuale noi, fără cuvinte.",
        "## Memorie de lucru  (Memoria cifrelor, Aritmetică)",
        "Păstrarea informației în minte câteva secunde, în timp ce faci ceva cu ea.",
        "## Viteză de procesare  (Căutare de simboluri, Codare)",
        "Cât de repede și de corect poți îndeplini sarcini vizuale simple.",
        "Fiecare domeniu se calculează din probele sale, iar rezultatul general din toate cele zece.",
    ]),
]

SCORES = [
    ("Cum funcționează scorurile", [
        "## Comparat cu persoane de vârsta ta",
        "Punctele obținute la o probă sunt comparate cu cele ale unui grup mare de persoane de vârsta ta. Un scor "
        "arată unde te situezi între ele, nu câte răspunsuri ai dat corect.",
        "## Probe, domenii și ansamblu",
        "Fiecare probă primește un scor, fiecare dintre cele patru domenii primește unul din probele sale, iar un "
        "rezultat general le reunește pe toate. Cam doi din trei oameni obțin un scor apropiat de medie la fiecare.",
        "## Percentilele",
        "Percentila 75 înseamnă că ai obținut un scor mai mare decât 75 din 100 de persoane de vârsta ta. Nu este "
        "procentul de răspunsuri corecte.",
        "## Intervale, nu puncte fixe",
        "Orice test are o eroare de măsurare, așa că rapoartele reale dau un interval de încredere în loc de un "
        "singur număr. O diferență mică între două scoruri nu înseamnă de obicei nimic.",
    ]),
    ("Scorurile din acest joc", [
        "## Calificative",
        "Probele, cele patru domenii și evaluarea completă primesc un calificativ de la D la S: D, C, B, A și S "
        "pentru cei mai buni dintre cei mai buni. Calificativul evaluării complete este Calificativul tău general. "
        "Standardele din spatele lor sunt create pentru acest joc, așa că îți arată doar propriul progres. Le poți "
        "ascunde din Setări.",
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
        "## „Scorul tău rămâne același toată viața.”",
        "Scorurile adulților sunt destul de stabile, dar nu bătute în cuie. Educația, sănătatea și împrejurările "
        "vieții contează, iar scorurile se pot schimba de-a lungul anilor.",
        "## „Antrenamentul cerebral te face mai inteligent.”",
        "Exersarea te face mai bun la sarcinile pe care le exersezi. Analize ample au găsit puține dovezi că "
        "progresul se transferă asupra inteligenței generale. Acest joc te va face mai bun la aceste puzzle-uri. "
        "Nu te va face mai inteligent.",
        "## „Un test online mi-a spus care e scorul meu real.”",
        "Evaluările reale sunt standardizate pe eșantioane mari, alese cu grijă, și se aplică în condiții "
        "controlate. Testele online, inclusiv acest joc, nu sunt, așa că rezultatele lor nu pot fi comparate cu "
        "scorurile reale.",
    ]),
    ("Mituri și adevăruri  (continuare)", [
        "## „Un scor la test arată cât valorezi.”",
        "Aceste teste măsoară un set anume de abilități de raționament, memorie și viteză. Nu spun nimic despre "
        "bunătate, creativitate, perseverență sau despre cea mai mare parte din ceea ce face ca o viață să "
        "meargă bine.",
        "## „O diferență mare între domeniile mele înseamnă că ceva nu e în regulă.”",
        "Diferențele clare între domenii sunt frecvente în populația generală. "
        "Doar un specialist calificat, privind întregul tablou, poate spune dacă un anumit profil contează.",
        "## „Scorurile cresc de la o generație la alta.”",
        "Parțial adevărat. Scorurile medii au crescut constant în secolul XX (efectul "
        "Flynn). Acesta este unul dintre motivele pentru care testele sunt renormate din când în când.",
    ]),
]

ABOUT = [
    ("Despre Puzzleth", [
        "Puzzleth este un joc de antrenament inspirat de structura și regulile de administrare ale evaluărilor "
        "cognitive individuale reale. Fiecare puzzle este generat de joc. Nu este folosit niciun item dintr-un "
        "test real, iar jocul nu este afiliat cu niciun editor de teste și nici susținut de vreunul.",
        "## Acesta nu este un test psihologic",
        "Calificativele sale provin din standarde aproximative create pentru acest joc. Nu pot fi comparate cu "
        "rezultatele unei evaluări reale, "
        "nu pot stabili niciun diagnostic și nu trebuie folosite pentru decizii școlare, profesionale, juridice "
        "sau medicale.",
        "## Pentru cine este",
        "Pentru cei care au emoții înaintea unei evaluări și vor să știe cum decurge. Pentru cei cărora le plac "
        "puzzle-urile grele. Și pentru oricine e curios cum funcționează aceste evaluări.",
    ]),
]

TOPICS = [
    ("expect", "La ce să te aștepți", EXPECT),
    ("subtests", "Cele zece probe", SUBTESTS),
    ("indexes", "Cele patru domenii", INDEXES),
    ("scores", "Cum se citesc scorurile", SCORES),
    ("myths", "Mituri și adevăruri", MYTHS),
    ("about", "Despre joc", ABOUT),
]
