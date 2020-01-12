# Sentence Boundary Detection

This repository **attempts** to detect sentence boundaries (which is messier than it appears at first sight).
It also **attempts** to apply sentence boundaries to html (which means dealing with markers).

# Limitations

Don't use this repository in production as it's not battle tested yet. Some functions seems brittle and error recovery is inexistent.
It has also only been tested or english.

# Approach

I tried my luck with a logistic regression on common patterns that can be observed both at the start and the end of a sentence.
I also added hardcoded.

# Results

On terminaison candidates (which are linebreaks, punctuation and special symbols (?!;:.), and also .".
The Logistic regression touts a 98% + classification success rate on both brown and wsj dataset.
But the model is not refined at all and work remains. Specifically: 
- Overlearning may be a reality, the common crossvalidation (intra or intercorpus) have not been done.
- Coefficients on the logistic regression have not been inspected at all. Some features could be excluded.
- Some rare (yet with a frequency that has to be determined) terminaison points were not considered by our model as valid candidates, hence they were not counted as missed as they should (this is a common pitfall, as pointed by the article cited at the end of the readme.

# Usage

## Installation

Use python 3.7 or later.
Explanation : f-strings are used and there are place where dictionaries are expected to be ordered (which is almost the case for 3.6, but without any warranties).


Install the dependencies with your favorite virtualenv manager. 
With venv :
```
python3 -m venv .venv --without-pip
source .venv/bin/activate # or .\venv\Scripts\activate on windows
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
pip install -r requirements.txt
```

With pipenv (given it's already installed)
```
pipenv install
```


##

## Dev


# Final notes

This repository has been set up for a recruitement pupose. I don't think I'll maintain it. If you fork it and do nice things, shout me an email so that I can publicize your fork on this Readme.

# ROADMAP

- Inspect and improve the model, use crossvalidation, inspect awesome fails (i.e couple of sentences where the model gives high confidenceand yet fails miserably)
- Test more thorougly html and text input, possibly with a generation mechanism.
- Refactor/Comment hard-to-reason-about functions


# Credits

Datasets from
```
Jonathon Read, Rebecca Dridan, Stephan Oepen, and Lars JØorgen Solberg.
2012a. Sentence boundary detection: A long solved problem? In Proceedings of COLING 2012: Posters, pages 985–994, Mumbai, India.
```



