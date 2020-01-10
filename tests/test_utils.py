import syspathfixer
import statistics
from sdb import utils
import pytest

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


def test_evaluate_candidates():

    result = list(utils.split_at_all_candidates(INPUT_STRING_UNSEGMENTED))

    boolean_evals = list(utils.evaluate_candidates(result, LIST_SEGMENTED))

    assert boolean_evals[0] is True
    assert sum(boolean_evals) == 4


def test_evaluate_candidates_on_real_data():
    for corpus in ["wsj", "brown"]:
        unsegmented_string = "".join(utils.read_unsegmented_corpus_iter(corpus))
        candidates_iterable = utils.split_at_all_candidates(unsegmented_string)
        segmented_iterable = utils.read_segmented_corpus_iter(corpus)

        booleans_iterable = utils.evaluate_candidates(
            candidates_iterable, segmented_iterable
        )

        m = statistics.mean(booleans_iterable)
        assert m > 0.5


# def test_extract_features():
