# CASS Dataset for Summarization

The code available in this repository allows to clean the CASS dataset and give the split use in
the paper 'STRASS: A Light and Effective Method for Extractive Summarization Based on Sentence Embeddings' (Bouscarrat et al., 2019)
that will appear in the [Student Research Workshop](https://sites.google.com/view/acl19studentresearchworkshop/accepted-papers) of ACL 2019.

# 1) Download

## 1.1) The data: French 'CASS dataset'
First, the data need to be download.
* Download the file starting with 'freemium_cass' (in our case we used the version 20180315).
This file can be accessed [here](ftp://echanges.dila.gouv.fr/CASS/).
Information about this dataset can be found [here](https://www.data.gouv.fr/fr/datasets/cass)).

```shell
wget ftp://echanges.dila.gouv.fr/CASS/Freemium_cass_global_20180315-170000.tar.gz
```

* Uncompress the file

## 1.2) Install the Spacy French module

The only module necessary is spacy and the model for the language of the documents. For the CASS dataset it's French.

```shell
python install spacy
python -m spacy download fr
```

or

```shell
conda install -c conda-forge spacy 
python -m spacy download fr
```


# 2)Preprocess the data

The preprocessing may need to be changed depending on the format of your data. The file preprocessing_CASS.py
is specifically made to work on the french CASS dataset.

Launch preprocessing_CASS.py with the path of your downloaded CASS dataset :

```shell
python3 preprocessing_CASS.py --data_dir path_to_your_data (--clean_dir path_to_clean_data)
```

Example:

```shell
python3 preprocessing_CASS.py --data_dir input_data/20180315-170000/
```

With this command all the cleaned files will be created in a repository called cleaned_files. It will contain
all the files with a text and at list one summary in a format like this:

```
sent_textA
sent_textB
sent_textC
@highlight
sent_sumA
sent_sumB
```

All the sentences are tokenized, lowercased and the accents are removed.

The --language is used to choose the version of spacy used to tokenize the dataset.