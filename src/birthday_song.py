"""Short personalized birthday greeting, spoken over instrumental music."""
CHORUS = """Today’s your day, the candles glow,
There’s someone special we all know.
<Name>, let’s celebrate with you,
With love and laughter all day through!
Happy Birthday <Name>!"""
SECTIONS = [('Birthday greeting', CHORUS)]


def personalized_sections(name):
    return [(heading, words.replace('<Name>', name)) for heading, words in SECTIONS]


def personalized_chorus(name):
    return CHORUS.replace('<Name>', name)
