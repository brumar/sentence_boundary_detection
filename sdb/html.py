import re

TEXT = 0
MARKUP = 1

LINE_BREAKERS = set(
    [
        "<address>",
        "<article>",
        "<aside>",
        "<blockquote>",
        "<canvas>",
        "<dd>",
        "<div>",
        "<dl>",
        "<dt>",
        "<fieldset>",
        "<figcaption>",
        "<figure>",
        "<footer>",
        "<form>",
        "<h1>",
        "<h2>",
        "<h3>",
        "<h4>",
        "<h5>",
        "<h6",
        "<header>",
        "<hr>",
        "<li>",
        "<main>",
        "<nav>",
        "<noscript>",
        "<ol>",
        "<p>",
        "<pre>",
        "<section>",
        "<table>",
        "<tfoot>",
        "<ul>",
        "<video>",
    ]
)
LINE_BREAKERS.add("<br>")
LINE_BREAKERS.add("<br/>")


def append_if_not_empty(l, s, markup_or_text):
    if markup_or_text not in (TEXT, MARKUP):
        raise ValueError
    if s:
        l.append((markup_or_text, s))


def markup_tokenise(html):
    end = 0
    output = []
    for match in re.finditer(r"<\s*[^>]*>", html, re.S):
        start = match.span()[0]
        append_if_not_empty(output, html[end:start], TEXT)
        end = match.span()[1]
        append_if_not_empty(output, html[start:end], MARKUP)
    append_if_not_empty(output, html[end:], TEXT)
    return output


def tokenized_to_text(tokenized):
    text = []
    for element in tokenized:
        if element[0] == TEXT:
            text.append(element[1])
        if element[0] == MARKUP and element[1] in LINE_BREAKERS:
            if text[-1:] != ["\n"]:
                text.append("\n")
    return "".join(text)


def surround_and_flatten(list_strings, start, end):
    output = []
    for s in list_strings:
        output.append(start + s + end)
    return "".join(output)


def next_or_none(iterator):
    if iterator is None:
        return None
    try:
        return next(iterator)
    except StopIteration:
        return None


def select_token(dictionary_iterators):
    weak = dictionary_iterators["weak"]
    strong = dictionary_iterators["strong"]
    both_MARKUP = kind(weak) == MARKUP and kind(strong) == MARKUP
    both_TEXT = kind(weak) == TEXT and kind(strong) == TEXT

    if (not both_MARKUP) and (not both_TEXT):
        if kind(weak) == MARKUP:
            # MARKUP has absolute priority over text
            return "weak"
        else:
            return "strong"
    elif both_TEXT:
        # in case of both text => the shortest win
        if len(val(strong)) <= len(val(weak)):
            return "strong"
        else:
            return "weak"
    elif both_MARKUP:
        # in case of both markup
        # close has the absolute priority

        # if both open => strong is chosen
        # but if both close => weak is chose
        # reversing the preference order is applied to avoid
        # <<open_1 open2 close1 close2>> pattern
        both_CLOSE = val(weak).startswith("</") and val(strong).startswith("</")
        both_OPEN = not val(weak).startswith("</") and not val(strong).startswith("</")
        if both_OPEN:
            return "strong"
        if both_CLOSE:
            return "weak"
        elif val(weak).startswith("</"):
            return "weak"
        else:
            return "strong"


def val(d):
    return d["value"][1]


def kind(d):
    return d["value"][0]


def iter_on(d):
    v = next_or_none(d["iterator"])
    if v is None:
        d["value"] = (d["value"][0], None)
    else:
        d["value"] = v


def get_unselected(selection):
    if selection == "weak":
        return "strong"
    return "weak"


def shave_redundant_text(dict_other, text_length):
    previous_value = val(dict_other)
    new_value = previous_value[text_length:]
    dict_other["value"] = (kind(dict_other), new_value)


def merge(html_weak, html_strong):
    output = []
    weak_tokens = iter(markup_tokenise(html_weak))
    strong_tokens = iter(markup_tokenise(html_strong))
    dictionary_iterators = {
        "weak": {"value": next_or_none(weak_tokens), "iterator": weak_tokens},
        "strong": {"value": next_or_none(strong_tokens), "iterator": strong_tokens},
    }
    stack_of_opened_markups = []
    stack_of_markup_to_re_open_asap = []
    while True:
        if None in (
            (val(dictionary_iterators["weak"]), val(dictionary_iterators["strong"]))
        ):
            break
        # print(dictionary_iterators)
        selection = select_token(dictionary_iterators)
        other = get_unselected(selection)
        dict_selected = dictionary_iterators[selection]
        dict_other = dictionary_iterators[other]

        if selection == "weak" and kind(dict_selected) == MARKUP:
            if not val(dict_selected).startswith("</"):
                stack_of_opened_markups.append(val(dict_selected))
            else:
                stack_of_opened_markups.pop(len(stack_of_opened_markups) - 1)

        if (
            selection == "strong"
            and kind(dict_selected) == MARKUP
            and val(dict_selected).startswith("</")
        ):
            for markup_to_close in reversed(stack_of_opened_markups):
                output.append("</" + markup_to_close[1:])
                stack_of_markup_to_re_open_asap.append(markup_to_close)
            stack_of_opened_markups = []

        output.append(val(dict_selected))
        if (
            selection == "strong"
            and kind(dict_selected) == MARKUP
            and not val(dict_selected).startswith("</")
        ):
            for markup_to_re_open in reversed(stack_of_markup_to_re_open_asap):
                output.append(markup_to_re_open)
                stack_of_opened_markups.append(markup_to_re_open)
            stack_of_markup_to_re_open_asap = []

        if kind(dict_selected) == TEXT:
            shave_redundant_text(dict_other, len(val(dict_selected)))
        iter_on(dict_selected)

    # Most probably, on single iterator stoped
    # The other has probably remaining values to yield
    val_weak = val(dictionary_iterators["weak"])
    val_strong = val(dictionary_iterators["strong"])

    if val_weak is None:
        output.append(val_strong)
        for v in dictionary_iterators["strong"]["iterator"]:
            output.append(v[1])

    if val_strong is None:
        output.append(val_weak)
        for v in dictionary_iterators["weak"]["iterator"]:
            output.append(v[1])

    return "".join(output)

    #
    # if current_s_token[0] == MARKUP:
    #     output.append(current_s_token[1])
    #     current_s_token = next_or_none(strong_tokens)
    # elif current_w_token[0] == MARKUP:
    #     output.append(current_w_token[1])
    #     current_w_token = next_or_none(weak_tokens)
    # elif len(current_s_token[1]) > len(current_w_token[1]):
    #     output.append(current_w_token[1])
    #     current_s_token = (TEXT, current_s_token[1][len(current_w_token[1]):])
    #     current_w_token = next_or_none(weak_tokens)
    # elif len(current_s_token[1]) < len(current_w_token[1]):
    #     output.append(current_s_token[1])
    #     current_w_token = (TEXT, current_w_token[1][len(current_s_token[1]):])
    #     current_s_token = next_or_none(strong_tokens)
    # elif current_s_token[1] == current_w_token[1]:
    #     output.append(current_s_token[1])
    #     current_s_token = next_or_none(strong_tokens)
    #     current_w_token = next_or_none(weak_tokens)
    # else:
    #     print(current_w_token, current_s_token)
    #     raise Exception
