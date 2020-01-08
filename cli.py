import click
import urllib.request
import os


@click.group()
def cli():
    pass


@cli.command()
@click.option("--force", help="force redownload", is_flag=True)
def download_corpus(force):
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


if __name__ == "__main__":
    cli()
