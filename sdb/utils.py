from typing import List
from itertools import islice


def read_segmented_corpus_iter(corpus):
    with open("./data/{corpus}/segmented.txt", "r") as f:
        line = f.readline()
        while line:
            yield line
            line = f.readline()
    

def raw_surroundings(lines: List[str])->List[tuple]:
    """capture last two cars and next two cars around
    terminaison point
    """
    for l, l2 in zip(islice(lines, 0, None), islice(lines, 1, None)):
        if len(l) > 2 and len(l2) > 0:
            last_letters_no_breaking_line = l[-3:-1]
            first_new_letter = l2[:1]
            yield (last_letters_no_breaking_line, first_new_letter)
