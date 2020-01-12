from typing import List, Iterable
from pathlib import Path
from sdb import features, html
import re
import numpy as np
from sklearn.metrics import roc_curve, auc
import nltk
import math
import pickle

file_path = Path(__file__)
project_directory = file_path.parent.parent

DATA_DIR = project_directory / Path("data")

CANDIDATES = ""
NORMAL_CANDIDATES = set([";", ":", ".", "!", "?"])


def read_unsegmented_corpus_iter(corpus: str):
    target = "unsegmented.txt"
    yield from _read_corpus(corpus, target)


def read_segmented_corpus_iter(corpus: str):
    target = "segmented.txt"
    yield from _read_corpus(corpus, target)


def read_abbrevs(lg="en"):
    output = {}
    filepath = DATA_DIR / Path("freqlist") / Path(lg) / Path(f"{lg}_full.txt")
    with open(filepath, "r") as f:
        for line in f:
            vals = line.split()
            if vals[0].endswith("."):
                vals[1] = int(vals[1])
                output[vals[0]] = round(math.log(vals[1]))
    return output


def _read_corpus(corpus, target):
    filepath = DATA_DIR / Path(corpus) / target
    with open(filepath, "r") as f:
        line = f.readline()
        while line:
            yield line
            line = f.readline()


def split_at_all_candidates(input_string_unsegmented: str) -> Iterable[str]:
    # tech debt warning
    # this behavior is tightly coupled with is_gold_findable
    # maintain both functions together
    ignore_next_car = False
    for line_loop in input_string_unsegmented.splitlines():
        line = "\n" + line_loop
        current_line = []
        for index_car, car in enumerate(line):
            if ignore_next_car:
                ignore_next_car = False
                continue
            current_line.append(car)
            if ((car == ".") and (index_car != len(line) - 1)) and (
                line[index_car + 1]
            ) == '"':
                current_line.append('"')
                # print("---------------")
                # print("".join(current_line))
                yield "".join(current_line)
                current_line = []
                ignore_next_car = True
            elif car in NORMAL_CANDIDATES:
                yield "".join(current_line)
                current_line = []
        if current_line:
            yield "".join(current_line)


def get_ending_line_patterns(candidate):
    output = {}
    for pattern in features.ENDING_LINE_PATTERNS:
        output[pattern] = re.search(pattern, candidate) is not None
    return output


def get_starting_line_patterns(candidate):
    output = {}
    for pattern in features.STARTING_LINE_PATTERNS:
        output[pattern] = re.search(pattern, candidate) is not None
    return output


def at_least_one_verb(candidate):
    tokens = re.findall(r"\w+", candidate)  # naive tokenizer
    pos = nltk.pos_tag(tokens)
    for p in pos:
        if p[1].startswith("V") or p[1] == "MD":
            return True
    return False


def get_interaction_patterns(starting_line_patterns, ending_line_patterns):
    return {
        features.MOST_COMMON_PATTERN: (
            starting_line_patterns[r"^\s?[A-Z]"] and ending_line_patterns[r"[a-z]\.$"]
        )
    }


def extract_feature_newline(candidates_list):

    # This feature extraction function has been built such as candidates evaluation
    # are postponed until next candidate has been processed
    # This whi
    for c, cand in enumerate(candidates_list):
        if c != 0:
            starting_line_patterns = get_starting_line_patterns(cand)
            interaction_patterns = get_interaction_patterns(
                starting_line_patterns, ending_line_patterns
            )
            # the first candidate is evaluated with its ending line pattern
            # as well as its starting line pattern

            newline = cand.startswith("\n")
            leading_whitespace = cand.startswith("\n ") or cand.startswith(" ")
            yield {
                features.LINEBREAK: newline,
                features.NEXT_LEADING_WHITESPACE: leading_whitespace,
                **ending_line_patterns,
                **starting_line_patterns,
                **interaction_patterns,
                features.NB_WORDS: nb_words,
            }
        ending_line_patterns = get_ending_line_patterns(cand)
        nb_words = len(re.findall(r"\w+", cand))

    # NOTE : TRy to remove this yield as the last sentence makes not sense to be evaluated
    # and the values are bunk anyway
    yield {
        features.LINEBREAK: True,
        features.NEXT_LEADING_WHITESPACE: True,
        **ending_line_patterns,
        **starting_line_patterns,
        **interaction_patterns,
        features.NB_WORDS: nb_words,
    }


def is_gold_findable(gold: str):
    # tech debt warning
    # this behavior is tightly coupled with split_at_all_candidates
    # maintain both functions together
    if gold.endswith('."'):
        return True
    if gold.endswith("\n"):
        return True
    if any((gold.endswith(x) for x in NORMAL_CANDIDATES)):
        return True
    return False


def evaluate_candidates(
    candidates: Iterable[str], list_result: Iterable[str]
) -> Iterable[bool]:
    """returns an iterable giving booleans evaluating if candidates match"""
    gold_iterator = iter(list_result)
    advance_gold_iterator = True
    buffer = ""
    for c, cand in enumerate(candidates):
        if not cand or cand.isspace():
            yield False
            continue
        if advance_gold_iterator:
            current_gold = advance_to_next_findable_gold(gold_iterator)
        buffer = buffer + cand.strip()

        # print("cand->",cand)
        # print("gold->", current_gold)
        # print("buff->",buffer)
        # print("--")
        if len(buffer) > 2000 or len(current_gold) > 2000:
            raise Exception

        # important : candidates may have extra white spaces or linebreaks
        # this is useful information for model training but they should be
        # stripped off to be properly be compared to gold standards which do
        # not include this information

        # as buffer and current gold can be the result of a concatenation with
        # uncontrolled whitespaces, we are better off
        # stripping all the whitespaces
        # on both string
        # as gold iterable and buffer iterable advance together,
        # the chances of false positive are unlikely
        # print(cand, current_gold)
        # import pdb; pdb.set_trace()
        if buffer.replace(" ", "") == current_gold.replace(" ", ""):
            buffer = ""
            yield True
            advance_gold_iterator = True
        else:
            yield False
            advance_gold_iterator = False


def advance_to_next_findable_gold(gold_iterator) -> str:
    try:
        current_gold = next(gold_iterator).strip()
        while not is_gold_findable(current_gold):
            current_gold = current_gold + next(gold_iterator).strip()
    except StopIteration:
        raise Exception(
            """Bug. the target sentences have all been passed but candidates remain.
                        This is likely an error in is_gold_findable function"""
        )
    return current_gold


def raw_surroundings(lines: Iterable[str]) -> List[tuple]:
    """capture last two cars and next two cars around
    terminaison point
    """
    previous_line = None
    for l in lines:
        if previous_line is not None:
            last_letters_no_breaking_line = previous_line[-3:-1]
            first_new_letters = l[:2]
            yield (last_letters_no_breaking_line, first_new_letters)
        previous_line = l


def build_array_from_features_iterable(features_dict):

    # totally unoptimized
    big_list = []

    for d, dic in enumerate(features_dict):
        values = dic.values()
        big_list.extend(values)
    n = len(values)
    return np.asarray(big_list).reshape((d + 1, n))


def raw_logistic_regression(features, labels):
    from sklearn.linear_model import LogisticRegression

    logmodel = LogisticRegression(max_iter=10000)
    logmodel.fit(features, labels)
    return logmodel


def prepare_dataset(corpus):
    unsegmented_string = "".join(read_unsegmented_corpus_iter(corpus))
    candidates = list(split_at_all_candidates(unsegmented_string))
    segmented = list(read_segmented_corpus_iter(corpus))
    booleans_iterable = evaluate_candidates(list(candidates), list(segmented))
    features_dic_iter = extract_feature_newline(candidates)
    array = build_array_from_features_iterable(features_dic_iter)
    labels = np.asarray(list(booleans_iterable))
    return array, labels


def segment_html(html_string, model):
    tokenized = html.markup_tokenise(html_string)
    full_text = html.tokenized_to_text(tokenized)
    result_full_text = segment(full_text, model)
    flat_segmented_html = html.surround_and_flatten(
        result_full_text, start='<span class="sentence">', end="</span>"
    )
    result = html.merge(html_string, flat_segmented_html)
    return [result]


def segment(unsegmented_string, model):
    candidates = list(split_at_all_candidates(unsegmented_string))
    features_dic_iter = extract_feature_newline(candidates)
    array = build_array_from_features_iterable(features_dic_iter)
    predictions = model.predict(array)
    output = []
    buffer = ""
    for candidate, prediction in zip(candidates, predictions):
        buffer += candidate.replace("\n", "")
        if prediction:
            output.append(buffer)
            buffer = ""
    if buffer:
        output.append(buffer)
    return output


def load_model(modelname):
    if not modelname.endswith(".pkl"):
        modelname += ".pkl"
    with open(f"./models/{modelname}", "rb") as f:
        return pickle.load(f)


def compute_precision(labels, logmodel, features):
    predictions = logmodel.predict(features)
    errors = 0
    for p, label in zip(predictions, labels):
        if p != label:
            errors += 1
    precision = 1 - (errors / len(predictions))
    return precision


def train_model_on_corpus(corpus):
    array, labels = prepare_dataset(corpus)
    logmodel = raw_logistic_regression(array, labels)
    precision = compute_precision(labels, logmodel, array)
    logmodel._sbd_precision = precision
    return logmodel


def save_model(model, output):
    with open(output, "wb") as f:
        pickle.dump(model, f)
