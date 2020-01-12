import syspathfixer
from sdb import html

inline_node = (
    'The <b><a href="/wiki/Lexington-Concord_Sesquicentennial_half_dollar" '
    'title="Lexington-Concord Sesquicentennial half dollar">Lexington-Concord '
    'Sesquicentennial half dollar</a></b> is a <a href="/wiki/Half_dollar_(United_States_coin)" '
    'title="Half dollar (United States coin)">fifty-cent piece</a>. And this is beautiful'
).replace("\n", "")
# stolen from wikipedia and edited to shorten and add a sentence


def test_ft_merger():
    to_be_merged = (
        '<span class="sentence">The Lexington-Concord Sesquicentennial half dollar is a fifty-cent piece.</span>'
        '<span class="sentence"> And this is beautiful</span>'
    ).replace("\n", "")

    result = html.merge(inline_node, to_be_merged)
    print(result)

    expected = (
        '<span class="sentence">The <b><a href="/wiki/Lexington-Concord_Sesquicentennial_half_dollar" '
        'title="Lexington-Concord Sesquicentennial half dollar">Lexington-Concord '
        'Sesquicentennial half dollar</a></b> is a <a href="/wiki/Half_dollar_(United_States_coin)" '
        'title="Half dollar (United States coin)">fifty-cent piece</a>.</span><span class="sentence"> '
        "And this is beautiful</span>"
    ).replace("\n", "")

    assert expected == result


def test_ut_text_markup_tokenisation():
    tokens = html.markup_tokenise("<a>text</a> <something>something</something>")
    assert tokens[-1] == (html.MARKUP, "</something>")
    assert tokens[1] == (html.TEXT, "text")
