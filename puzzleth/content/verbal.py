"""Item banks for the verbal subtests, grouped into six difficulty tiers.

Similarities: each category yields many word pairs. The answers mirror real examiner scoring:
  2 pts - the abstract, general category ("Both are fruits")
  1 pt  - a concrete shared property ("Both can be eaten")
  0 pts - wrong, overly general, or only true of one word.
"""
import sys

# tier: [(members, two_point, one_point, near_miss_zero)]
SIMILARITIES = {
    1: [
        (["apple", "banana", "orange", "pear", "peach", "plum", "cherry", "grape"],
         "Both are fruits", "Both can be eaten", "Both are vegetables"),
        (["red", "blue", "green", "yellow", "purple"],
         "Both are colors", "You can see both in a rainbow", "Both are shapes"),
        (["dog", "cat", "hamster", "rabbit", "goldfish"],
         "Both are animals kept as pets", "Both can live in a house", "Both are wild animals"),
        (["fork", "spoon", "knife", "chopsticks"],
         "Both are eating utensils", "Both are kept in a kitchen drawer", "Both are writing tools"),
        (["shirt", "sock", "coat", "hat", "glove", "scarf"],
         "Both are articles of clothing", "Both are made of cloth", "Both are pieces of furniture"),
        (["Monday", "Friday", "Sunday", "Wednesday", "Tuesday"],
         "Both are days of the week", "Both are on a calendar", "Both are months"),
    ],
    2: [
        (["chair", "table", "sofa", "bed", "desk", "bookshelf"],
         "Both are pieces of furniture", "Both are found in a house", "Both are tools"),
        (["car", "bus", "train", "bicycle", "boat", "airplane"],
         "Both are means of transportation", "Both can carry people", "Both are toys"),
        (["piano", "violin", "drum", "flute", "trumpet", "guitar"],
         "Both are musical instruments", "Both make noise", "Both are electronic devices"),
        (["elbow", "knee", "wrist", "ankle", "shoulder", "hip"],
         "Both are joints", "Both are parts of the body", "Both are bones"),
        (["rain", "snow", "hail", "sleet"],
         "Both are forms of precipitation", "Both fall from the sky", "Both are kinds of clouds"),
        (["hammer", "saw", "screwdriver", "wrench", "drill"],
         "Both are tools", "Both are made of metal", "Both are weapons"),
    ],
    3: [
        (["anger", "joy", "fear", "sadness", "surprise", "disgust"],
         "Both are emotions", "Both show on your face", "Both are illnesses"),
        (["inch", "mile", "meter", "foot", "yard", "kilometer"],
         "Both are units of length", "Both are marked on a ruler or map", "Both are units of weight"),
        (["sight", "hearing", "smell", "taste", "touch"],
         "Both are senses", "Both use a part of your body", "Both are thoughts"),
        (["minute", "hour", "second", "week", "month"],
         "Both are units of time", "Both are shown on a clock or calendar", "Both are distances"),
        (["Mars", "Venus", "Jupiter", "Saturn", "Mercury"],
         "Both are planets", "Both are in the sky", "Both are stars"),
        (["newspaper", "magazine", "encyclopedia", "radio"],
         "Both are sources of information", "People read or listen to both", "Both are things you write with"),
    ],
    4: [
        (["poem", "statue", "painting", "symphony", "novel"],
         "Both are works of art", "Both are made by people", "Both are kinds of music"),
        (["democracy", "monarchy", "dictatorship", "republic"],
         "Both are forms of government", "Both have leaders", "Both are countries"),
        (["coal", "oil", "natural gas", "wood"],
         "Both are fuels — sources of energy", "Both can be burned", "Both are metals"),
        (["telephone", "letter", "email", "telegram"],
         "Both are means of communication", "People use both to reach others far away", "Both are languages"),
        (["seed", "egg", "embryo", "bud"],
         "Both are early stages of a living thing", "Both are small", "Both are animals"),
        (["hunger", "thirst", "fatigue"],
         "Both are signals of a bodily need", "Both feel uncomfortable", "Both are diseases"),
    ],
    5: [
        (["honesty", "courage", "kindness", "loyalty", "patience"],
         "Both are virtues — moral qualities", "Both are good things", "Both are emotions"),
        (["fly", "tree", "mushroom", "whale", "moss"],
         "Both are living organisms", "Both grow", "Both are insects"),
        (["steam", "ice", "fog", "dew"],
         "Both are forms of water", "Both can be found outdoors", "Both are gases"),
        (["vaccine", "antibiotic", "bandage", "surgery"],
         "Both are medical treatments", "Both are found in a hospital", "Both are illnesses"),
        (["friend", "enemy", "ally", "rival"],
         "Both describe relationships between people", "Both are people you know", "Both are family members"),
        (["map", "blueprint", "diagram", "model"],
         "Both are representations of something", "Both are drawn or built by people", "Both are buildings"),
    ],
    6: [
        (["freedom", "justice", "equality", "peace"],
         "Both are ideals a society strives for", "Both are good things to have", "Both are laws"),
        (["permit", "forbid", "require"],
         "Both are ways of regulating behavior", "Both are things parents say", "Both mean yes"),
        (["fact", "theory", "hypothesis"],
         "Both are claims about how the world is", "Both appear in science books", "Both are always true"),
        (["reward", "punishment", "praise"],
         "Both are consequences that shape behavior", "Both are given by parents or teachers", "Both are feelings"),
        (["birth", "death", "marriage"],
         "Both are major life transitions", "Both happen to people", "Both are sad"),
        (["space", "time"],
         "Both are dimensions in which events are located", "Both are very big", "Both are measured in meters"),
    ],
}

SIMILARITIES_GENERIC_ZERO = [
    "Both are things", "Both are words", "Both have names", "They are different", "Both exist",
    "Both start with a letter",
]

# tier: [(word, precise 2-pt definition, vague/partial 1-pt definition)]
VOCABULARY = {
    1: [
        ("bed", "A piece of furniture for sleeping on", "Something soft in your bedroom"),
        ("ship", "A large boat that carries people or goods over water", "Something that floats"),
        ("penny", "A coin worth one cent", "A kind of money"),
        ("winter", "The coldest season of the year", "When it snows"),
        ("breakfast", "The first meal of the day", "Something you eat"),
        ("repair", "To fix something that is broken", "To work on something"),
        ("slice", "A thin, flat piece cut from something larger", "A piece of pizza"),
        ("yesterday", "The day before today", "Some time ago"),
    ],
    2: [
        ("assemble", "To fit the parts of something together", "To make something"),
        ("enormous", "Extremely large in size", "Big"),
        ("consume", "To eat, drink, or use up", "To have something"),
        ("terminate", "To bring to an end", "To fire someone from a job"),
        ("hesitate", "To pause before acting because of uncertainty", "To be slow"),
        ("fragile", "Easily broken or damaged", "Made of glass"),
        ("ancient", "Belonging to the very distant past", "Like something in a museum"),
        ("remember", "To bring back to mind from the past", "To think"),
    ],
    3: [
        ("reluctant", "Unwilling and hesitant", "Not happy about something"),
        ("compassion", "Sympathetic concern for the suffering of others", "Being nice"),
        ("ponder", "To think about something carefully", "To wonder"),
        ("obstruct", "To block or get in the way of", "To stop"),
        ("migrate", "To move from one region to another, often seasonally", "To fly south"),
        ("domestic", "Relating to the home or to one's own country", "A house"),
        ("tranquil", "Calm and free from disturbance", "Quiet"),
        ("summarize", "To give a brief statement of the main points", "To write something"),
    ],
    4: [
        ("sanctuary", "A place of refuge or safety", "A church"),
        ("evasive", "Tending to avoid direct answers or commitment", "Sneaky"),
        ("ominous", "Giving the impression that something bad will happen", "Dark and scary"),
        ("plagiarize", "To present someone else's work as your own", "To copy"),
        ("tangible", "Able to be touched; real and concrete", "Something you own"),
        ("diverse", "Showing a great deal of variety", "Different"),
        ("infer", "To conclude something from evidence and reasoning", "To guess"),
        ("mediate", "To help opposing sides reach an agreement", "To be in the middle"),
    ],
    5: [
        ("audacious", "Showing a bold willingness to take risks", "Rude"),
        ("ephemeral", "Lasting for a very short time", "Delicate"),
        ("pragmatic", "Dealing with things sensibly and realistically", "Smart"),
        ("meticulous", "Showing great attention to detail", "Neat"),
        ("ubiquitous", "Present or found everywhere", "Popular"),
        ("benevolent", "Well-meaning and kindly", "Rich"),
        ("candid", "Truthful and straightforward; frank", "Unposed, like a photo"),
        ("consensus", "General agreement among a group", "A vote"),
    ],
    6: [
        ("obfuscate", "To deliberately make something unclear", "To hide"),
        ("perfunctory", "Carried out with minimal effort or care", "Quick"),
        ("tacit", "Understood or implied without being stated", "Quiet"),
        ("sagacious", "Having keen judgment and wisdom", "Old"),
        ("ameliorate", "To make something bad better", "To change"),
        ("equivocate", "To use ambiguous language to avoid committing", "To lie"),
        ("recalcitrant", "Stubbornly uncooperative with authority", "Angry"),
        ("quixotic", "Exceedingly idealistic; unrealistic and impractical", "Strange"),
        ("esoteric", "Understood by only a small group with special knowledge", "Weird"),
    ],
}

# tier: [(question, answer, [distractors])]
INFORMATION = {
    1: [
        ("How many days are in a week?", "7", ["5", "6", "8"]),
        ("What do bees make?", "Honey", ["Milk", "Silk", "Butter"]),
        ("How many months are in a year?", "12", ["10", "11", "13"]),
        ("What is frozen water called?", "Ice", ["Steam", "Fog", "Salt"]),
        ("What do you call a baby dog?", "A puppy", ["A kitten", "A calf", "A foal"]),
        ("In which direction does the sun rise?", "East", ["West", "North", "South"]),
        ("How many legs does a spider have?", "8", ["6", "4", "10"]),
        ("What color do you get by mixing blue and yellow?", "Green", ["Purple", "Orange", "Brown"]),
    ],
    2: [
        ("What is the largest ocean on Earth?", "The Pacific", ["The Atlantic", "The Indian", "The Arctic"]),
        ("Who wrote \"Romeo and Juliet\"?", "William Shakespeare", ["Charles Dickens", "Mark Twain", "Jane Austen"]),
        ("How many continents are there?", "7", ["5", "6", "8"]),
        ("What is the capital of France?", "Paris", ["Lyon", "Marseille", "Brussels"]),
        ("What gas do plants absorb from the air to make food?", "Carbon dioxide", ["Oxygen", "Nitrogen", "Helium"]),
        ("At sea level, water boils at how many degrees Celsius?", "100", ["90", "120", "212"]),
        ("Which planet is known as the Red Planet?", "Mars", ["Venus", "Jupiter", "Mercury"]),
        ("How many sides does a hexagon have?", "6", ["5", "7", "8"]),
    ],
    3: [
        ("Who painted the Mona Lisa?", "Leonardo da Vinci", ["Michelangelo", "Raphael", "Vincent van Gogh"]),
        ("What is the chemical symbol for gold?", "Au", ["Ag", "Gd", "Go"]),
        ("On which continent is Egypt?", "Africa", ["Asia", "Europe", "South America"]),
        ("Who was the first President of the United States?", "George Washington",
         ["Thomas Jefferson", "Abraham Lincoln", "John Adams"]),
        ("What is the capital of Japan?", "Tokyo", ["Kyoto", "Osaka", "Seoul"]),
        ("Which organ pumps blood through the body?", "The heart", ["The lungs", "The liver", "The kidneys"]),
        ("How many players does one soccer team have on the field?", "11", ["9", "10", "12"]),
        ("What is the largest planet in our solar system?", "Jupiter", ["Saturn", "Neptune", "Earth"]),
    ],
    4: [
        ("In what year did World War II end?", "1945", ["1939", "1918", "1950"]),
        ("Who developed the theory of relativity?", "Albert Einstein", ["Isaac Newton", "Niels Bohr", "Galileo Galilei"]),
        ("What is the hardest natural substance?", "Diamond", ["Quartz", "Iron", "Granite"]),
        ("What is the capital of Australia?", "Canberra", ["Sydney", "Melbourne", "Perth"]),
        ("Who wrote \"On the Origin of Species\"?", "Charles Darwin",
         ["Gregor Mendel", "Louis Pasteur", "Alfred Wegener"]),
        ("Which language has the most native speakers?", "Mandarin Chinese", ["English", "Spanish", "Hindi"]),
        ("What is the smallest prime number?", "2", ["1", "3", "0"]),
        ("In a human cell, where is most of the DNA found?", "The nucleus",
         ["The membrane", "The ribosome", "The cytoplasm"]),
    ],
    5: [
        ("Who wrote \"One Hundred Years of Solitude\"?", "Gabriel García Márquez",
         ["Jorge Luis Borges", "Pablo Neruda", "Isabel Allende"]),
        ("What is the capital of Canada?", "Ottawa", ["Toronto", "Montreal", "Vancouver"]),
        ("What does the abbreviation DNA stand for?", "Deoxyribonucleic acid",
         ["Dinitrogen acid", "Deoxyribose nitrate", "Dynamic nuclear acid"]),
        ("Which Wonder of the Ancient World stood in Alexandria?", "The Lighthouse (Pharos)",
         ["The Colossus", "The Hanging Gardens", "The Mausoleum"]),
        ("Absolute zero is approximately how many degrees Celsius?", "−273", ["−100", "−459", "−173"]),
        ("Who composed the opera \"The Magic Flute\"?", "Wolfgang Amadeus Mozart",
         ["Ludwig van Beethoven", "Giuseppe Verdi", "Richard Wagner"]),
        ("Which element has atomic number 1?", "Hydrogen", ["Helium", "Oxygen", "Carbon"]),
        ("What is the longest bone in the human body?", "The femur", ["The tibia", "The humerus", "The spine"]),
    ],
    6: [
        ("Who wrote \"Faust\"?", "Johann Wolfgang von Goethe", ["Friedrich Schiller", "Franz Kafka", "Thomas Mann"]),
        ("What is the approximate speed of light in a vacuum?", "300,000 km per second",
         ["30,000 km per second", "3,000,000 km per second", "300 km per second"]),
        ("Which philosopher wrote \"Critique of Pure Reason\"?", "Immanuel Kant",
         ["G. W. F. Hegel", "René Descartes", "David Hume"]),
        ("What is the capital of Kazakhstan?", "Astana", ["Almaty", "Tashkent", "Bishkek"]),
        ("In what year did the Berlin Wall fall?", "1989", ["1991", "1985", "1961"]),
        ("Who described planets moving in elliptical orbits?", "Johannes Kepler",
         ["Nicolaus Copernicus", "Tycho Brahe", "Ptolemy"]),
        ("What is the most abundant gas in Earth's atmosphere?", "Nitrogen", ["Oxygen", "Argon", "Carbon dioxide"]),
        ("Mansa Musa ruled which empire?", "The Mali Empire", ["The Songhai Empire", "The Ottoman Empire",
                                                              "The Aksumite Empire"]),
    ],
}


def bank(language):
    """The item banks written for ``language``: this module for English, otherwise verbal_<language>.

    The other languages have their own words and questions rather than translations of these, so that
    each item is as natural and as hard in that language as the English one is in English."""
    from . import verbal_fr, verbal_ro
    return {"ro": verbal_ro, "fr": verbal_fr}.get(language, sys.modules[__name__])
