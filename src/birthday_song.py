"""User-supplied birthday lyrics. Piper narrates these; it does not sing."""
CHORUS = """Happy birthday, <Name>, hooray, hooray!
We’re so glad to share your special day.
Make a wish and let your smile shine through,
<Name>, this birthday song is just for you!"""
SECTIONS = [
('Verse 1', """Today’s your day, the candles glow,
There’s someone special we all know.
<Name>, let’s celebrate with you,
With love and laughter all day through!"""),
('Chorus', CHORUS),
('Verse 2', """Another year, new dreams to chase,
New memories and a warm embrace.
May every step bring something new,
And may good friends walk beside you!"""),
('Chorus', CHORUS),
('Bridge', """Clap your hands and sing along,
Everybody join this birthday song!
Cut the cake, let’s give a cheer,
Here’s to <Name> and a wonderful year!"""),
('Final Chorus', """Happy birthday, <Name>, hooray, hooray!
May love and laughter always come your way!"""),
]

def personalized_sections(name):
    return [(heading, words.replace('<Name>',name)) for heading,words in SECTIONS]

def personalized_chorus(name):
    return CHORUS.replace('<Name>',name)
