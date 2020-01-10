from typing import List, Iterable
from pathlib import Path
from sdb import features

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


def extract_feature_newline(candidates_list):
    for c, cand in enumerate(candidates_list):
        if c == 0:
            continue
        newline = cand.startswith("\n")
        yield {features.LINEBREAK: newline}
    yield {features.LINEBREAK: True}


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
