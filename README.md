# Sentence Boundary Detection

This repository **attempts** to detect [sentence boundaries](https://en.wikipedia.org/wiki/Sentence_boundary_disambiguation) (which is an harder problem than it appears at first sight).
It also **attempts** to apply sentence boundaries to html (which means dealing with markers).

# Limitations

Don't use this repository in production as it's not battle tested yet. Some functions seems brittle and error recovery is inexistent.
It has also only been tested or english.


# Usage

Be warned that there is not setting files. If you need a different behavior (set of features, tweaks on the HTML output), you have to edit the source code itself.

## Installation

Use python 3.7 or later. Check it with
```
python3 --version
```

Explanation : f-strings are used and there are place where dictionaries are expected to be ordered (which is almost the case for 3.6, but without any warranties).


Install the dependencies with your favorite virtualenv manager. 
Unless you have better options, I favor using venv as follow :
```
python3 -m venv .venv --without-pip
source .venv/bin/activate # or .\venv\Scripts\activate on windows
wget https://bootstrap.pypa.io/get-pip.py  # or manually download it on windows
python3 get-pip.py
python3 -m pip install -r requirements.txt
```

With pipenv (taking as granted that it's already installed)
```
pipenv install
pipenv shell
```

## Train the Model

It's required to train the model before leveraging it.
First download the resources (thanks to Read & Al. 2012 for exposing clean datasets in the open).
Given your dependencies installed and your virtualenv activated.

```
python cli.py download-resources
```

Train the logistic regression on brown or wsj
```
python cli.py train brown --modelname myfirstmodel
```

## Use the Model

Use your model to segment text file

```
python cli.py segment ./examples/boll.txt --modelname mymodel > boll_output.txt
python cli.py segment ./examples/boll.html --modelname mymodel > boll_output.html
```
Or without stdout redirection (the "> file" part) if you prefer to see the result in your shell.


## Run the tests

Few tests have been put in place.
Run it with
```
pytest
```
To avoid long running tests (which are running on the whole wsj/brown corpus), you can use the dedicated marker to filter these tests out
```
pytest -m "not long"
```

# Information about the model

# Approach

I tried my luck with a [logistic regression](https://en.wikipedia.org/wiki/Logistic_regression) on common patterns that can be observed both at the start and the end of a sentence and also other features.

I picked the logistic regression for convenience (I know this kind of model). I chose to not dig too much into the state-of-the-art approaches for the sake of the "challenge" to come to a solution myself.

Patterns of sentences terminaison can be found in the `features.py` file. 
They have been also handpicked and hardcoded after an explorative phase. I did not take time to assess their importance. But I started with only these features which granted around 90% + success rate.

I also added handpicked hardcoded abbreviations (advice from the wikipedia page) and also added a numerical feature (number of words).
Both improved the model on both corpus.


# Results

On terminaison candidates (which are linebreaks, punctuation and special symbols (?!;:.), and also .".
The Logistic regression touts a 98% + classification success rate on both brown and wsj dataset.
But the model is not refined at all and work remains. Specifically: 
- Overlearning may be a reality, the common crossvalidation (intra or intercorpus) have not been done.
- Coefficients on the logistic regression have not been inspected at all. Some features could be excluded.
- Some rare (yet with a frequency that has to be determined) terminaison points were not considered by our model as valid candidates, hence they were not counted as missed as they should (this is a common pitfall, as pointed by the article cited at the end of the readme.

# Notes

## Messy notes

You can find some mess reflecting some of my ideas (in order to keep track of the thoughts during the exercice) in the exploration subfolder (a journal of ideas and an exploratory jupyter notebook).


## Final notes

This repository has been set up for a recruitement pupose. I don't think I'll maintain it. If you fork it and do nice things, shout me an email so that I can publicize your fork on this Readme.

## TODOS

- Normalization step user inputs (more on this in the quoted article).
- Treat gracefully erroneous input (like unexisting files)
- Inspect and improve the model, use crossvalidation, inspect awesome fails (i.e couple of sentences where the model gives high confidenceand yet fails miserably)
- Plot the ROC curve !
- Test more thorougly html and text input, possibly with a generation mechanism.
- Refactor/Comment hard-to-reason-about functions
- Separate dev requirements (black, pytest, jupyter) from user requirements
- Dokerize the application
- As the number of words is an important feature, it may be useful to classify with a multi layer approach like.
- Adapt the classifier so that False positive may be more damaging than False negative. Maybe set the coefficient for the feature "number of words" to a fixed level, a bit higher than its trained value. 


## Credits

Datasets were taken from http://svn.delph-in.net/odc/ put in place by these authors :
```
Jonathon Read, Rebecca Dridan, Stephan Oepen, and Lars JØorgen Solberg.
2012a. Sentence boundary detection: A long solved problem? In Proceedings of COLING 2012: Posters, pages 985–994, Mumbai, India.
```



