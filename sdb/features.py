LINEBREAK = 1
NEXT_LEADING_WHITESPACE = 2
NB_WORDS = 3
MOST_COMMON_PATTERN = 4  # end. High case
PUNCTUATION_SIGNS_CLASS = "[.!?\\-]"
P = PUNCTUATION_SIGNS_CLASS
_ENDING_LINE_PATTERNS = [
    r"[a-z]\.",
    r"[A-Z]\.",
    r"\d\.",
    r"\)\.",
    r"\"\.",
    r"\.\"",
    r"\?",
    r"\!",
    r"\:",
    r";",
    r"\w\w",
    r"%\.",
    r"(Mr\.)|(Ms\.)|(Mrs\.)|(Dr\.)",
]
ENDING_LINE_PATTERNS = [p + "$" for p in _ENDING_LINE_PATTERNS]

_STARTING_LINE_PATTERNS = [r"\d", r"[A-Z]", r"[a-z]", r"\"", r"\(", r"-"]
STARTING_LINE_PATTERNS = [r"^\s?" + p for p in _STARTING_LINE_PATTERNS]


# t.  |  ".  |  t;  |  t?  |  1.  |  tt  |  "?  |  t!  |  ).  |  t:  |  "!  |  T.  |  1;  |  --
