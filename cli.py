import click
import urllib.request
import os
from sdb import utils


freqlist = "https://raw.githubusercontent.com/hermitdave/FrequencyWords/master/content/2018/en/en_full.txt"


@click.group()
def cli():
    pass


@cli.command()
@click.option("--force", help="force redownload", is_flag=True)
def download_ressources(force):
    """get the WSJ corpus and brown corpus (segmented and unsegmented)"""
    # source : Sentence boundary detection: A long solved problem? J.Read 2012

    for corpus in ["wsj", "brown"]:
        if not os.path.exists(f"./data/{corpus}"):
            os.makedirs(f"./data/{corpus}")
        for seg_type in ["segmented", "unsegmented"]:
            url = f"http://svn.delph-in.net/odc/trunk/{corpus}/{seg_type}.txt"
            output = f"./data/{corpus}/{seg_type}.txt"
            if not os.path.exists(output) or force:
                urllib.request.urlretrieve(url, output)

    # NOTE : finally not that usefull => commented out

    # if not os.path.exists(f"./data/freqlist/en"):
    #     os.makedirs(f"./data/freqlist/en")
    # output = f"./data/freqlist/en/en_full.txt"
    # if not os.path.exists(output) or force:
    #     urllib.request.urlretrieve(freqlist, output)


@cli.command()
@click.argument("corpus")
@click.option("--modelname", help="model name (for saving purpose)")
def train(corpus=None, modelname=None):
    if corpus is None:
        corpus = "brown"
    if modelname is None:
        modelname = "brown.pkl"
    else:
        modelname = modelname + ".pkl"

    print("please wait few minutes")
    model = utils.train_model_on_corpus(corpus)
    if not os.path.exists(f"./models/"):
        os.mkdir("./models")
    model_output = f"./models/{modelname}"
    utils.save_model(model, model_output)
    print(
        f"model has been trained on brown corpus, with a {model._sbd_precision:.3f}"
        f" success rate on the classification on special characters (?!;:.)"
        f"on the full dataset"
    )
    print(
        f"use the model on your sentences with"
        f" python cli.py segment <<inputfile.txt>> --modelname {modelname}"
    )


@cli.command()
@click.argument("input")
@click.option("--modelname", help="model name")
@click.option("--ishtml", help="is the input html", is_flag=True)
def segment(input, modelname, ishtml=False):
    if modelname is None:
        print("--modelname is necessary")
        return
    string_input = []
    with open(input, "r") as finput:
        for line in finput:
            string_input.append(line)
    string_input = "".join(string_input)
    model = utils.load_model(modelname)
    if not ishtml:
        result = utils.segment(string_input, model)
    else:
        result = utils.segment_html(string_input, model)
    for line in result:
        print(line.strip())


if __name__ == "__main__":
    cli()
