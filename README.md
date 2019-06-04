# CASS Dataset for Summarization

The code available in this repository allows to clean the 

# 1) Download

## 1.1) The data: French 'CASS dataset'
First, the data need to be download.
* Download the file starting with 'freemium_cass' (in our case we used the version 20180315).
This file can be accessed [here](ftp://echanges.dila.gouv.fr/CASS/).
Information about this dataset can be find [here](https://www.data.gouv.fr/fr/datasets/cass)).

```shell
wget ftp://echanges.dila.gouv.fr/CASS/Freemium_cass_global_20180315-170000.tar.gz
```

* Uncompress the file

## 1.2) 


# 2)Preprocess the data
## 2.1) Clean the data : French 'cours de Cassation dataset'

The preprocessing may need to be changed depending on the format of your data. The file preprocessing_CASS.py
is specifically made to work on the french CASS dataset.

Launch preprocessing_CASS.py with the path of your downloaded CASS dataset :

```shell
python3 data/preprocessing_CASS.py --data_dir path_to_your_data --clean_dir path_to_clean_data --no_split
```

Example:

```
python3 data/preprocessing_CASS.py --data_dir input_data/20180315-170000/ --clean_dir cleaned_data --no_split
```

All the files containing the necessary information will be in the --clean_dir path.

## 2.2) Tokenize 

Now to tokenize the texts the function make_datafiles.py will be used:

```shell
python3 data/make_datafiles.py --data_dir path_to_your_data --tokenized_dir path_to_tokenized_files --language lang
```

Examples:
```shell
python3 data/make_datafiles.py --data_dir cleaned_data/ --tokenized_dir tokenized_data --language fr
```

The --language is used to choose the version of spacy used to tokenize the dataset.