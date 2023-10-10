"""
Module to extract the texts and the summaries of the XML files present in the
downloaded folder

This code is partially based on the code of abisee in the repo:
https://github.com/abisee/cnn-dailymail
"""

import argparse
import hashlib
import logging
import os
import re
import sys
import unicodedata

import spacy

###############################################################################

LOGGER = logging.getLogger(__name__)
END_TOKENS = [";", "!", r"\?"]  # acceptable ways to end a sentence

###############################################################################


def init_parser():
    """
    Parser for the arguments
    """
    parser = argparse.ArgumentParser(
        description="Preprocessing of the data to \
                                                  avoid documents with not all\
                                                  the informations"
    )
    parser.add_argument("--data_dir", help="Folder with the data inside", required=True)
    parser.add_argument(
        "--clean_dir",
        help="Folder where the clean files will\
                                             be",
        default="cleaned_files",
    )
    args = vars(parser.parse_args())
    return args


def get_text_summary(path, name):
    """
    Take a path and a filename as input and
    output a text and a summary.
    :param path: a string containing a path
    :param name: a strig
    """

    with open(
        os.path.join(path, name), "r", encoding="utf-8", errors="ignore"
    ) as myfile:
        full_text = myfile.read()
        text = None
        summary = None
        # Looking if there is some content and a summary
        if re.search(
            "<CONTENU>.*</CONTENU>\n</BLOC.*<ANA.*>.*</ANA>", full_text, re.DOTALL
        ):
            # Getting the content and cleaning it
            search = re.search(
                "(?<=<CONTENU>).*?(?=</CONTENU>\n</BLOC)", full_text, re.DOTALL
            )
            text = search.group(0)
            text = re.sub("<p>|</p>|<br.*?/>|null", "", text)
            text = re.sub("^\n", "", text)
            text = re.sub("\n+", "\n", text)
            text = re.sub("\n$", "", text)
            if not re.search(r".*(null)*\S+.*", text, re.DOTALL):
                return text, summary
            # Getting all the summaries (some times there is several) and
            # cleaning them
            search = re.findall("<ANA.*?>.*?(?=</ANA>)", full_text, re.DOTALL)
            summary = "\n".join(search)
            summary = re.sub("<ANA.*?>|<b>|</b>|null", "", summary)
            summary = re.sub(" +", " ", summary)
            summary = re.sub(r"\s\s+|\n ", "\n", summary)
            summary = re.sub("^\n", "", summary)
            summary = re.sub("\n+", "\n", summary)
            summary = re.sub("\n$", "", summary)

    return text, summary


def tokenize_stories(text, summary, doc_name, tokenized_stories_dir, nlp):
    """
    Tokenize a file using Spacy Tokenizer
    :param text: a string
    :param summary: a string
    :param doc_name: a string
    :param tokenized_stories_dir: a str with the path where the clean data
    will be created
    :param nlp: a Spacy model
    """

    story = text + "\n@highlight" + summary
    res = ""
    doc = nlp(story)
    for token in doc:
        res += token.text + " "
    # res = ' '.join(res)
    res = res.lower()
    res = strip_accents(res)
    res = fix_missing_new_line(res)
    with open(os.path.join(tokenized_stories_dir, doc_name), "w") as output:
        output.write(res)


def hashhex(string):
    """
    Returns a heximal formated SHA1 hash of the input string.
    :param s: a string
    :return h.hexdigest(): a heximal formated SHA1
    """
    hash_str = hashlib.sha1()
    hash_str.update(string.encode())
    return hash_str.hexdigest()


def get_url_hashes(url_list):
    """
    Returns a list containing the hashed input urls
    :param url_list: a list of string
    :return hash_list: a list of hashed string
    """
    return [hashhex(url) for url in url_list]


def fix_missing_period(line):
    """
    Adds a period to a line that is missing a period
    :param line: a string containing a line
    :return line: a string
    """
    if "@highlight" in line:
        return line
    if line == "":
        return line
    if line[-1] in END_TOKENS:
        return line
    # print line[-1]
    return line + " ."


def fix_missing_new_line(text):
    """
    Adds a new line when it's necessary
    :param text: a string
    :return text_fix: a string
    """
    text = text.replace("....", "... .")
    text = text.replace(". . .", "...")
    text = re.sub(r"(?<=\S) \. (?=\d)", ".", text)
    text = re.sub(r"(?<=\d) , (?=\d)", ",", text)
    for elem in END_TOKENS:
        text = re.sub(" " + elem + r"\s+", " " + elem + "\n", text)
    text = text.replace(r"\.", ".")
    text = text.replace(r"\?", "?")
    text = re.sub(" +", " ", text)
    text = re.sub(r"\s\s+", "\n", text)
    text = re.sub(r"(?<= \S) \.\.\.", "...", text)
    text = text.replace("\n+", "\n")
    text_fix = re.sub("\n*@highlight", "\n@highlight", text)
    return text_fix


def strip_accents(text):
    """
    Replace the accented letters by their equivalent without
    accent
    :param text: a string
    :return str(text): a string
    """
    try:
        text = unicode(text, "utf-8")
    except NameError:  # unicode is a default on python 3
        pass
    text = unicodedata.normalize("NFD", text)
    text = text.encode("ascii", "ignore")
    text = text.decode("utf-8")
    text = text.replace("@highlight", "[HIGHLIGHT]", 1)
    text = text.replace("@highlight", "")
    text = text.replace("[HIGHLIGHT]", "@highlight")
    text = text.replace("\n@highlight ", "\n@highlight\n")
    return str(text)


def main():
    """
    Clean the files and put the extracted items in a new file
    """
    args = init_parser()

    data_dir = args["data_dir"]
    if not os.path.exists(args["clean_dir"]):
        os.mkdir(args["clean_dir"])
    path_story = args["clean_dir"]

    nlp = spacy.load("fr_core_news_sm", disable=["ner", "tagger", "parser"])

    number_files = 0

    # Search in all the subdirectories to find all the documents
    for path, _, files in os.walk(data_dir):
        for name in files:
            text, summary = get_text_summary(path, name)

            if (
                not text
                or not summary
                or not re.search(r".*(null)*\S+.*", summary, re.DOTALL)
            ):
                break

            doc_name = name.replace(".xml", ".story")

            tokenize_stories(text, summary, doc_name, path_story, nlp)

            number_files += 1
            if number_files % 10000 == 0:
                LOGGER.info("%d files found", number_files)

    LOGGER.info("Number of files: %d", number_files)
    return 0


if __name__ == "__main__":
    sys.exit(main())
