import sys
from pathlib import Path

file_path = Path(__file__)
project_directory = file_path.parent.parent
sys.path.append(str(project_directory))
# DIRTY TRICK SO THAT sdb module can be found by manipulating PYTHONPATH


from sdb import utils
import pytest


@pytest.fixture
def ten_sentences_brown():
    with open("./tests/data_fixtures/ten_sentences_brown.txt", "r") as f:
        yield f.readlines()


def test_view_surroundings_end_sentences(ten_sentences_brown):
    surroundings = list(utils.raw_surroundings(ten_sentences_brown))
    assert len(surroundings) == 9, "no surroundings for last sentence"
    assert tuple(surroundings[0]) == ("T.", "\nT")
    assert tuple(surroundings[1]) == ("d.", "\nT")
