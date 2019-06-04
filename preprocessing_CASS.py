import argparse
import logging
import os
import random as rd
import re
import sys

###############################################################################

LOGGER = logging.getLogger(__name__)

###############################################################################


def init_parser():
    '''
    Parser for the arguments
    '''
    parser = argparse.ArgumentParser(description='Preprocessing of the data to \
                                                  avoid documents with not all\
                                                  the informations')
    parser.add_argument('--data_dir', help='Folder with the data inside',
                        required=True)
    parser.add_argument('--clean_dir', help='Folder where the clean files will\
                                             be', default='cleaned_files')
    parser.add_argument('--split', dest='split', action='store_true',
                        help='Generate new split train/valid/test')
    parser.add_argument('--no_split', dest='split', action='store_false',
                        help='No new split are generated')
    parser.set_defaults(split=False)
    parser.add_argument('--file_list_dir', help='Folder with the list of \
                                                different files inside',
                        default='file_lists_fr')
    args = vars(parser.parse_args())
    return args


def init_result_folder(folder_save):
    '''
    Function that creates the folder if needed or remove
    the old splits
    '''
    if not os.path.exists(folder_save):
        os.mkdir(folder_save)

    all_train_files = os.path.join(folder_save, "all_train.txt")
    all_valid_files = os.path.join(folder_save, "all_val.txt")
    all_test_files = os.path.join(folder_save, "all_test.txt")

    # Deletion of the old files with the list of the documents
    if os.path.exists(all_train_files):
        os.remove(all_train_files)
    if os.path.exists(all_valid_files):
        os.remove(all_valid_files)
    if os.path.exists(all_test_files):
        os.remove(all_test_files)


def write_exist(filename):
    '''
    Function that append if the file exists or
    create a new one if it doesn't
    '''
    if os.path.exists(filename):
        return 'a'  # append if already exists
    else:
        return 'w'  # make a new file if not


def get_text_summary(path, name):
    '''
    Function that takes a path and a filename as input and
    output a text and a summary.
    '''

    with open(os.path.join(path, name), 'r', encoding='utf-8',
              errors='ignore') as myfile:

        full_text = myfile.read()
        text = None
        summary = None
        # Looking if there is some content and a summary
        if re.search('<CONTENU>.*</CONTENU>\n</BLOC.*<ANA.*>.*</ANA>',
                     full_text, re.DOTALL):
            url_page = name.replace('.xml', '')

            # Getting the content and cleaning it
            search = re.search('(?<=<CONTENU>).*?(?=</CONTENU>\n</BLOC)',
                               full_text, re.DOTALL)
            text = search.group(0)
            text = re.sub('<p>|</p>|<br.*?/>|null', '', text)
            text = re.sub('^\n', '', text)
            text = re.sub('\n+', '\n', text)
            text = re.sub('\n$', '', text)
            if not(re.search('.*(null)*\S+.*', text, re.DOTALL)):
                return text, summary
            # Getting all the summaries (some times there is several) and
            # cleaning them
            search = re.findall('<ANA.*?>.*?(?=</ANA>)', full_text, re.DOTALL)
            summary = '\n'.join(search)
            summary = re.sub('<ANA.*?>|<b>|</b>|null', '', summary)
            summary = re.sub('( +)', ' ', summary)
            summary = re.sub('\s\s+|\n ', '\n', summary)
            summary = re.sub('^\n', '', summary)
            summary = re.sub('\n+', '\n', summary)
            summary = re.sub('\n$', '', summary)

    return text, summary


def random_choice_split(text, summary, folder_save, train, valid, test):

    all_train_files = os.path.join(folder_save, "all_train.txt")
    all_valid_files = os.path.join(folder_save, "all_val.txt")
    all_test_files = os.path.join(folder_save, "all_test.txt")

    part = rd.randint(0, 9)

    if 0 <= part <= 7:
        with open(all_train_files, write_exist(all_train_files),
                  encoding='utf-8') as myfile:
            myfile.write(url_page+"\n")
        train += 1
        LOGGER.info("Find a file, %s, go into train, %d file in train" %
                    (url_page, train))

    elif part == 8:
        with open(all_valid_files, write_exist(all_valid_files),
                  encoding='utf-8') as myfile:
            myfile.write(url_page+"\n")

        valid += 1
        LOGGER.info("Find a file, %s, go into valid, %d file in valid" %
                    (url_page, valid))

    else:
        with open(all_test_files, write_exist(all_test_files),
                  encoding='utf-8') as myfile:
            myfile.write(url_page+"\n")
        test += 1
        LOGGER.info("Find a file, %s, go into test, %d file in test" %
                    (url_page, test))
    return train, valid, test


def main():
    args = init_parser()

    data_dir = args['data_dir']
    split = args['split']
    if not os.path.exists(args['clean_dir']):
        os.mkdir(args['clean_dir'])
    path_story = args['clean_dir']

    # Folder where to save the files with the distribution of the documents
    folder_save = args['file_list_dir']

    if split:
        init_result_folder(folder_save)

    train = 0
    test = 0
    valid = 0
    number_files = 0

    # Search in all the subdirectories to find all the documents
    for path, subdirs, files in os.walk(data_dir):
        for name in files:
            text, summary = get_text_summary(path, name)

            if not(text) or not(summary) or \
               not(re.search('.*(null)*\S+.*', summary, re.DOTALL)):
                break

            number_files += 1
            if split:
                train, valid, test = random_choice_split(text, summary,
                                                         folder_save)

            filename = name.replace('.xml', '')

            with open(os.path.join(path_story, filename+".story"), "w",
                      encoding='utf-8') as myfile:
                myfile.write(text+'\n'+"@highlight\n"+summary)

            if number_files % 10000 == 0:
                LOGGER.info("%d files found" % number_files)

    LOGGER.info('Number of files: %d' % number_files)

if __name__ == "__main__":
    sys.exit(main())
