import argparse
import collections
import hashlib
import logging
import os
import re
import struct
import sys
import unicodedata

import spacy

###############################################################################

LOGGER = logging.getLogger(__name__)
END_TOKENS = [';', '!', '\?']  # acceptable ways to end a sentence

###############################################################################


def init_parser():
    # Parser for the arguments
    parser = argparse.ArgumentParser(description='Preprocessing of the data with \
                                                the tokenization')
    parser.add_argument('--data_dir', help='Folder with the data inside',
                        default='clean_cassa')
    parser.add_argument('--tokenized_dir', help='Folder where the tokenized files \
                                                 will be',
                        default='tokenized_data')
    parser.add_argument('--language', help='Language of the files',
                        default='fr')
    args = vars(parser.parse_args())
    return args


def tokenize_stories(stories_dir, tokenized_stories_dir, nlp):
    """
    Maps a whole directory of .story files to
    a tokenized version using Spacy Tokenizer
    """
    LOGGER.info("Preparing to tokenize %s to %s..." %
                (stories_dir, tokenized_stories_dir))
    stories = os.listdir(stories_dir)

    LOGGER.info("Tokenizing %i files in %s and saving in %s..." %
                (len(stories), stories_dir, tokenized_stories_dir))
    for s in stories:
        with open(os.path.join(stories_dir, s), 'r', encoding='utf-8') \
                as input_f,\
                open(os.path.join(tokenized_stories_dir, s), 'w') as output:
            res = ''
            doc = nlp(input_f.read())
            for token in doc:
                res += token.text + ' '
            # res = ' '.join(res)
            res = res.lower()
            res = strip_accents(res)
            res = fix_missing_new_line(res)
            output.write(res)

    # Check that the tokenized stories directory contains the same number of
    # files as the original directory
    num_orig = len(os.listdir(stories_dir))
    num_tokenized = len(os.listdir(tokenized_stories_dir))
    if num_orig != num_tokenized:
        raise Exception("The tokenized stories directory %s contains %i files,\
                        but it should contain the same number as %s \
                        (which has %i files). Was there an error \
                        during tokenization?" %
                        (tokenized_stories_dir, num_tokenized,
                         stories_dir, num_orig))
    LOGGER.info("Successfully finished tokenizing %s to %s.\n" %
                (stories_dir, tokenized_stories_dir))


def read_text_file(text_file):
    lines = []
    with open(text_file, "r", encoding='utf-8') as f:
        for line in f:
            lines.append(line.strip())
    return lines


def hashhex(s):
    """Returns a heximal formated SHA1 hash of the input string."""
    h = hashlib.sha1()
    h.update(s.encode())
    return h.hexdigest()


def get_url_hashes(url_list):
    return [hashhex(url) for url in url_list]


def fix_missing_period(line):
    """Adds a period to a line that is missing a period"""
    if "@highlight" in line:
        return line
    if line == "":
        return line
    if line[-1] in END_TOKENS:
        return line
    # print line[-1]
    return line + " ."


def fix_missing_new_line(text):
    """Adds a new line when it's necessary"""
    text = text.replace('....', '... .')
    text = text.replace('. . .', '...')
    text = re.sub('(?<=\S) \. (?=\d)', '.', text)
    text = re.sub('(?<=\d) , (?=\d)', ',', text)
    for elem in END_TOKENS:
        text = re.sub(' '+elem+'\s+', ' '+elem+'\n', text)
    text = text.replace('\.', '.')
    text = text.replace('\?', '?')
    text = re.sub(' +', ' ', text)
    text = re.sub('\s\s+', '\n', text)
    text = re.sub('(?<= \S) \.\.\.', '...', text)
    text = text.replace('\n+', '\n')
    text = re.sub('\n*@highlight', '\n@highlight', text)
    return text


def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError as e:  # unicode is a default on python 3
        LOGGER.error(e)
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    text = text.replace('@highlight', '[HIGHLIGHT]', 1)
    text = text.replace('@highlight', '')
    text = text.replace('[HIGHLIGHT]', '@highlight')
    text = text.replace('\n@highlight ', '\n@highlight\n')
    return str(text)


def main():

    args = init_parser()
    data_dir = args['data_dir']
    data_tokenized_dir = args['tokenized_dir']
    lang = args['language']

    nlp = spacy.load(lang, disable=['ner', 'tagger', 'parser'])

    finished_files_dir = "finished_files"

    # Create some new directories
    if not os.path.exists(data_tokenized_dir):
        os.makedirs(data_tokenized_dir)
    if not os.path.exists(finished_files_dir):
        os.makedirs(finished_files_dir)

    # Run stanford tokenizer on both stories dirs, outputting to tokenized
    # stories directories
    tokenize_stories(data_dir, data_tokenized_dir, nlp)


if __name__ == "__main__":
    sys.exit(main())
