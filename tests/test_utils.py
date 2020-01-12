import syspathfixer
import statistics
from sdb import utils, features
import pytest
import numpy as np


# DIRTY TRICK SO THAT sdb module can be found by manipulating PYTHONPATH

INPUT_STRING_UNSEGMENTED = "".join(
    [
        "candidates can have various forms! Why using only punctuations?",
        (
            "Observations on corpus seems to find that ; and : "
            "can be potential candidates too! There is also"
        ),
        (
            ' a special case, the "special case." Here the'
            "real termination point should be the quote."
        ),
    ]
)
LIST_SEGMENTED = [
    "candidates can have various forms!",
    "Why using only punctuations?",
    (
        "Observations on corpus seems to find "
        "that ; and : can be potential candidates too!"
    ),
    'There is also a special case, the "special case."',
    'Here the real termination point should be the quote."',
]


@pytest.fixture
def ten_sentences_brown():
    with open("./tests/data_fixtures/ten_sentences_brown.txt", "r") as f:
        yield f.readlines()


def test_view_surroundings_end_sentences(ten_sentences_brown):
    surroundings = list(utils.raw_surroundings(ten_sentences_brown))
    assert len(surroundings) == 9, "no surroundings for last sentence"
    assert tuple(surroundings[0]) == ("e.", "Th")
    assert tuple(surroundings[1]) == ("d.", "Th")


def test_get_all_candidates():

    result = list(utils.split_at_all_candidates(INPUT_STRING_UNSEGMENTED))
    assert len(result) == 7
    assert result[0].strip() == "candidates can have various forms!"
    assert result[-2].strip() == 'There is also a special case, the "special case."'


def test_abbreviations_parsing():
    abbrevs = utils.read_abbrevs()
    assert len(abbrevs) > 100
    assert "dr." in abbrevs.keys()
    assert "mr." in abbrevs.keys()


def test_evaluate_candidates():

    result = list(utils.split_at_all_candidates(INPUT_STRING_UNSEGMENTED))

    boolean_evals = list(utils.evaluate_candidates(result, LIST_SEGMENTED))

    assert boolean_evals[0] is True
    assert sum(boolean_evals) == 4


@pytest.mark.long
def test_evaluate_candidates_on_real_data():
    for corpus in ["wsj", "brown"]:
        unsegmented_string = "".join(utils.read_unsegmented_corpus_iter(corpus))
        candidates_iterable = utils.split_at_all_candidates(unsegmented_string)
        segmented_iterable = utils.read_segmented_corpus_iter(corpus)

        booleans_iterable = utils.evaluate_candidates(
            candidates_iterable, segmented_iterable
        )

        m = statistics.mean(booleans_iterable)
        assert m > 0.40


def test_extract_feature_ends_with_newline():
    multiline_input = """lines break are important
    lines break may be hint. May very well be.
    they should be considered as a feature"""

    expectations = [True, False, True, True]

    candidates_list = list(utils.split_at_all_candidates(multiline_input))
    assert len(candidates_list) == 4

    feature_dict_list = list(utils.extract_feature_newline(candidates_list))
    assert len(feature_dict_list) == 4
    for fdic, expected in zip(feature_dict_list, expectations):
        assert fdic.get(features.LINEBREAK, False) is expected


def test_extract_feature_patterns_before():
    multiline_input = """lines break are important
 lines break may be hint. May very well be.
they should be considered as a feature"""
    print(multiline_input)

    expectations_breaks = [True, False, True, True]
    expectations_spaces = [True, True, False, True]

    candidates_list = list(utils.split_at_all_candidates(multiline_input))
    assert len(candidates_list) == 4

    feature_dict_list = list(utils.extract_feature_newline(candidates_list))
    assert len(feature_dict_list) == 4
    for fdic, expected_b, expected_s in zip(
        feature_dict_list, expectations_breaks, expectations_spaces
    ):
        assert fdic.get(features.LINEBREAK, False) is expected_b
        assert fdic.get(features.NEXT_LEADING_WHITESPACE, False) is expected_s


def test_extract_feature_patterns_next_line():
    multiline_input = """lines break are important
lines break may be hint. May very well be! "Do you think I just repeated myself ".
they should be considered as a feature"""
    candidates_list = list(utils.split_at_all_candidates(multiline_input))
    assert len(candidates_list) == 5
    feature_dict_list = list(utils.extract_feature_newline(candidates_list))
    for dic in feature_dict_list:
        sum = 0
        for pattern_line_start in features.STARTING_LINE_PATTERNS:
            if dic[pattern_line_start]:
                sum += 1
        assert sum <= 2, "each line at most one starting pattern and one ending pattern"

    assert feature_dict_list[0][r"\w\w$"] is True
    assert feature_dict_list[0][r"^\s?[a-z]"] is True
    assert feature_dict_list[2][r"\!$"] is True


@pytest.mark.long
def test_prepare_np_structures_on_real_data():
    for corpus in ["wsj", "brown"]:
        unsegmented_string = "".join(utils.read_unsegmented_corpus_iter(corpus))
        candidates = list(utils.split_at_all_candidates(unsegmented_string))
        segmented = list(utils.read_segmented_corpus_iter(corpus))

        booleans_iterable = utils.evaluate_candidates(list(candidates), list(segmented))
        features_dic_iter = utils.extract_feature_newline(candidates)

        array = utils.build_array_from_features_iterable(features_dic_iter)
        assert array.shape[1] == (
            len(features.ENDING_LINE_PATTERNS)
            + len(features.STARTING_LINE_PATTERNS)
            + 4
        )
        assert array.shape[0] > 1000

        labels = np.asarray(list(booleans_iterable))
        labels.reshape(1, array.shape[0])


@pytest.mark.long
def test_logistic_regression():
    for corpus in ["wsj", "brown"]:
        array, labels = utils.prepare_dataset(corpus)
        logmodel = utils.raw_logistic_regression(array, labels)
        precision = utils.compute_precision(labels, logmodel, array)
        assert precision > 0.95
