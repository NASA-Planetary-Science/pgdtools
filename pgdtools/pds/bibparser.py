"""Take a bibtex library file and produce an OLAF copy/pastable txt file.

The goal of this file is not that it is especially beautiful, but that we can
easily copy entries and then paste them again. Output is in the following format
for every entry:

--------------------------------

Lastname first Author

Number of Authors

Lastname second author if more than one author

Publication year

Reference text

DOI (if available, otherwise N/A

--------------------------------
"""

from pathlib import Path
from typing import List, Tuple

import bibtexparser
from bibtexparser.bparser import BibTexParser
import bibtexparser.customization as bibcust

BIBFILE = Path("../data/pgd_references.bib")


def process_bib_file(savename: Path = Path("pgd_library_olaf.txt")):
    """Process the bib file and save out an OLAF compatible txt file."""

    def customizations(record):
        record = bibcust.convert_to_unicode(record)
        record = bibcust.author(record)
        return record

    with open(BIBFILE) as bibtex_file:
        parser = BibTexParser()
        parser.customization = customizations
        db = bibtexparser.load(bibtex_file, parser=parser)

    with open(savename, "w") as fout:
        for it, entry in enumerate(db.entries):
            authors = format_authors(entry["author"])
            fout.write(authors[0][0])
            fout.write("\n\n")
            fout.write(f"{len(authors)}")
            fout.write("\n\n")
            if len(authors) > 1:
                fout.write(authors[1][0])
                fout.write("\n\n")
            fout.write(entry["year"])
            fout.write("\n\n")

            if entry["ENTRYTYPE"] == "article":
                ref_text = format_article(entry)
            elif entry["ENTRYTYPE"] == "inproceedings":
                ref_text = format_inproceedings(entry)
            elif entry["ENTRYTYPE"] == "phdthesis":
                ref_text = format_phdthesis(entry)

            fout.write(ref_text)
            fout.write("\n\n")
            try:
                fout.write(entry["doi"])
                fout.write("\n\n")
            except KeyError:
                pass
            fout.write("--------------------------------")
            fout.write("\n\n")


def clean_str(inp: str):
    """Clean up the string.

    Replace multiple dashes with single dash.
    Replace '\textmu ' with 'µ'
    Remove '\emph', '\textsuperscript' and '\textsubscript' from the string.

    :param inp: Input string

    :return: Cleaned string
    """
    inp = inp.replace("---", "-")
    inp = inp.replace("--", "-")
    inp = inp.replace("\\textmu ", "µ")
    inp = inp.replace("\\emph", "")
    inp = inp.replace("\\textsuperscript", "")
    inp = inp.replace("\\textsubscript", "")
    return inp


def format_authors(authors: List[str]) -> List[Tuple[str, str]]:
    """Format author list.

    Take the author list in form 'Lastname, Firstname Initial and Secondln, Fn Initial'
    and return a list of authors, each line containing a tuple of (Lastname, F.I.).

    :return: Lastname, Firstnames formatted according to my specs.
    """
    ret_val = []
    for author in authors:
        auth_split = author.split(",")
        if len(auth_split) == 2:
            lastname, tmp = auth_split
        if len(auth_split) == 3:  # we have a Jr or something!
            lastname = "".join(auth_split[0:2])
            tmp = auth_split[-1]

        tmp = tmp.strip().split()  # now all the first names individually
        fn_list = []
        for fn in tmp:
            if fn == "O'D.":  # The C.M.O'D. Alexander expception
                fn_list.append(fn)
            else:
                fn_list.append(f"{fn[0]}.")
        firstname = "".join(fn_list)

        ret_val.append((lastname, firstname))
    return ret_val


def format_article(entry):
    """Format a bibtexparser entry article as a string."""
    authors = format_authors(entry["author"])
    ref_text = ""
    for it, author in enumerate(authors):
        if it == 0:  # first author
            ref_text += f"{author[0]}, {author[1]}, "
        elif it == len(authors) - 1:
            ref_text += f"and {author[1]} {author[0]}, "
        else:
            ref_text += f"{author[1]} {author[0]}, "
    ref_text += clean_str(entry["title"]) + ", "
    ref_text += entry["journal"] + ", "
    ref_text += "Vol. " + entry["volume"] + ", "
    try:
        ref_text += "No. " + entry["number"] + ", "
    except KeyError:
        pass
    ref_text += "pp. " + entry["pages"].replace("--", "-") + ", "
    ref_text += entry["year"] + "."  # last entry, no comma
    return ref_text


def format_inproceedings(entry):
    """Format a bibtexparser entry inproceedings as a string."""
    authors = format_authors(entry["author"])
    ref_text = ""
    for it, author in enumerate(authors):
        if it == 0:  # first author
            ref_text += f"{author[0]}, {author[1]}, "
        elif it == len(authors) - 1:
            ref_text += f"and {author[1]} {author[0]}, "
        else:
            ref_text += f"{author[1]} {author[0]}, "
    ref_text += clean_str(entry["title"]) + ", "
    ref_text += entry["booktitle"] + ", "
    ref_text += "pp. " + entry["pages"].replace("--", "-") + ", "
    ref_text += entry["year"] + "."  # last entry, no comma
    return ref_text


def format_phdthesis(entry):
    """Format a bibtexparser entry phdthesis as a string."""
    authors = format_authors(entry["author"])
    ref_text = ""
    for it, author in enumerate(authors):
        if it == 0:  # first author
            ref_text += f"{author[0]}, {author[1]}, "
        elif it == len(authors) - 1:
            ref_text += f"and {author[1]} {author[0]}, "
        else:
            ref_text += f"{author[1]} {author[0]}, "
    ref_text += clean_str(entry["title"]) + ", "
    ref_text += entry["school"] + ", "
    ref_text += entry["year"] + "."  # last entry, no comma
    return ref_text


if __name__ == "__main__":
    process_bib_file()
