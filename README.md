# Sentence Boundary Detection

This repository **attempts** to detect [sentence boundaries](https://en.wikipedia.org/wiki/Sentence_boundary_disambiguation) (which is a harder problem than it appears at first sight).
It also **attempts** to apply its algorithm to segment html (surrounding sentences with `<span class="sentence">[...]</span>`

Don't use this repository in production as it's not battle tested yet. Some functions seem brittle and error recovery is absent. There are more mature tool out there like [nltk punkt](https://www.nltk.org/api/nltk.tokenize.html).

It has also only been tested on the english language.

The HTML feature will respect existing inline tags (e.g `span`, `strong` ...). If a sentence partially overlaps with such tags, they will be closed and reopened. But this behavior **will mess** with blocking tags such as p, div et...

In the future : 
- Sentence detection will occur only inside HTML sections that contains not a single blocking tags
- An opening blocking tag such as `<p>` will be interpreted as linebreak.

Be warned that there are no setting files. If you need a different behavior (set of features, tweaks on the HTML output), you have to edit the source code itself.

# Usage

## Installation

Use python 3.7 or later. Check it with :
```
$ python3 --version
```

Explanation : f-strings are used and there are places where dictionaries are expected to be ordered (which is almost the case for 3.6, but without strong warranties).


Install the dependencies with your favorite virtualenv manager. 
Unless you have better options, I advocate for using using venv as follows:
```
$ python3 -m venv .venv --without-pip
$ source .venv/bin/activate # or .\venv\Scripts\activate on windows
$ wget https://bootstrap.pypa.io/get-pip.py  # or manually download it on windows
$ python3 get-pip.py
$ python3 -m pip install -r requirements.txt
```

Alternatively, you can use [pipenv](https://github.com/pypa/pipenv) (taking as granted that it's already installed)
```
$ pipenv --python=3.7 install
$ pipenv shell
```

## Train the Model

It's required to train the model before using it.
First download the resources (thanks to Read & Al. 2012 for exposing clean datasets in the open, ref at the end).
Given your dependencies installed and your virtualenv activated,
```
$ python cli.py download-corpus
```

Train the logistic regression on [brown](https://en.wikipedia.org/wiki/Brown_Corpus) or [wsj](https://catalog.ldc.upenn.edu/LDC2000T43) corpus.
```
$ python cli.py train brown --modelname myfirstmodel
```

## Use the Model

Use your model to segment a text file.
Output of txt files will be represented as one sentence per line.
Output for html files will contains amended html with `<span class="sentence">` markups

```
$ python cli.py segment ./examples/boll.txt --modelname myfirstmodel > boll_output.txt
$ python cli.py segment ./examples/boll.html --modelname myfirstmodel --ishtml > boll_output.html
```
(Or without stdout redirection (the "> file" part) if you prefer to see the result in your shell)



# For developpers


## Run the tests

Few tests have been put in place.
Run it with
```
$ pytest
```
To avoid long running tests (which are running on the whole wsj/brown corpus), you can use the dedicated marker to filter these tests out
```
$ pytest -m "not long"
```

## Style

[black](https://black.readthedocs.io/) and [flake8](http://flake8.pycqa.org/en/latest/) has been used (following this [tutorial](https://ljvmiranda921.github.io/notebook/2018/06/21/precommits-using-black-and-flake8/))

# For Data Science People

# Approach

I tried my luck with a [logistic regression](https://en.wikipedia.org/wiki/Logistic_regression) on common patterns that can be observed both at the start and the end of a sentence and also other features.

I picked the logistic regression for convenience (I know this kind of model). I chose to not dig too much into the state-of-the-art approaches for the sake of the "challenge" to come to a solution myself.

Patterns of sentences termination can be found in the `features.py` file. 
They have been also handpicked and hardcoded after an explorative phase. I did not take time to assess their importance. But I started with only these features, which granted around 90% + success rate.

I also added handpicked hardcoded abbreviations (advice from the wikipedia page) and also added a numerical feature (number of words).
Both improved the model on both corpus.


# Results

On termination candidates (which are linebreaks, punctuation and special symbols (?!;:.), and also .".
The Logistic regression **touts a 98%+ classification success rate** on both brown and wsj dataset.
But the model is not refined at all and work remains. Specifically: 
- Over-learning may be a reality, the common cross-validation step (intra or inter-corpus) has not been done.
- Coefficients in the logistic regression have not been inspected at all. Some features could be excluded.
- Some rare (yet with a frequency that has to be determined) termination points were not considered by our model as valid candidates, hence they were not counted as missed as they should (this is a common pitfall, as pointed by the article cited at the end of the readme).

# Notes

## Messy notes

You can find some mess reflecting some of my ideas (in order to keep track of the thoughts during the exercice) in the exploration subfolder (a journal of ideas and an exploratory jupyter notebook).


## Final notes

This repository has been set up for a recruitement purpose. I don't think I'll invest time to properly maintain it. If you fork it and do nice things, shout me an email so that I can publicize your fork on this Readme.

## TODOS And Ideas

- Treat gracefully erroneous input (like unfindable files)
- Turn dictionnary iterators.
- Inspect and improve the model, use crossvalidation, inspect awesome fails (i.e couples of sentences where the model gives high confidence and yet fails miserably)
- Normalisation step on user inputs of unicode characters (cf article at the end of the readme).
- Plot the ROC curve !
- Test more thoroughly html and text input, possibly with a generation mechanism.
- Refactor/Comment hard-to-reason-about functions
- Separate dev requirements (black, pytest, jupyter) from user requirements
- Dokerize the application.
- As the "number of words" is an important feature, it may be useful to classify with a multi pass approach to conservatively accept candidates as sentences on a first pass, then progressively accept more and more sentences.
- Consider that False positive may be more damaging than False negative and adapt the classifier. Maybe setting the coefficient for the feature "number of words" to a fixed level, a bit more impactful than its trained value.
- Use beautiful soup instead of naive markup detection using regexes.
- Consider false posivite patterns such as the ellipis (...)
- Train on the more datasets (such as the other datasets exposed by Read. & al)


## Credits

Datasets were taken from http://svn.delph-in.net/odc/ put in place by these authors :
```
Jonathon Read, Rebecca Dridan, Stephan Oepen, and Lars JØorgen Solberg.
2012a. Sentence boundary detection: A long solved problem? In Proceedings of COLING 2012: Posters, pages 985–994, Mumbai, India.
```



