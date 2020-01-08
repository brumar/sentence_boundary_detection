from typing import List, Iterable
from itertools import islice
from pathlib import Path

file_path = Path(__file__)
project_directory = file_path.parent.parent

DATA_DIR = project_directory / Path("data")


def read_segmented_corpus_iter(corpus):
    filepath = DATA_DIR / Path(corpus) / "segmented.txt"
    with open(filepath, "r") as f:
        line = f.readline()
        while line:
            yield line
            line = f.readline()
    

def raw_surroundings(lines: Iterable[str])->List[tuple]:
    """capture last two cars and next two cars around
    terminaison point
    """
    for l, l2 in zip(islice(lines, 0, None), islice(lines, 1, None)):
        if len(l) > 2 and len(l2) > 0:
            last_letters_no_breaking_line = l[-3:-1]
            first_new_letter = l2[:1]
            yield (last_letters_no_breaking_line, first_new_letter)
