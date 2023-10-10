from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
import numpy as np
from pathlib import Path
import random

from sklearn.model_selection import train_test_split


def main() -> None:
    args = get_args()
    split_sum = args.train_size + args.val_size + args.test_size
    assert (
        split_sum <= 1.0
    ), f"train-size ({args.train_size}) + val-size ({args.val_size}) + test-size ({args.test_size}) = {split_sum} > 1.0"
    
    cleaned_files_dir = Path(args.cleaned_files_dir).expanduser().resolve()
    data_split_dir = Path(args.data_split_dir).expanduser().resolve()
    data_split_dir.mkdir(exist_ok=True, parents=True)

    file_ids = [
        file_path.name.replace(".story", "")
        for file_path in cleaned_files_dir.iterdir()
    ]

    train_ids, test_ids = train_test_split(
        file_ids,
        train_size=args.train_size,
        test_size=args.val_size + args.test_size,
        random_state=42,
    )
    val_ids, test_ids = train_test_split(
        test_ids,
        test_size=args.test_size / (args.val_size + args.test_size),
        random_state=42,
    )

    train_ids_fp = data_split_dir/"all_train.txt"
    list_to_file(train_ids, train_ids_fp)
    print(f"Training IDs saved to {train_ids_fp}")

    val_ids_fp = data_split_dir/"all_val.txt"
    list_to_file(val_ids, val_ids_fp)
    print(f"Validation IDs saved to {val_ids_fp}")

    test_ids_fp = data_split_dir/"all_test.txt"
    list_to_file(test_ids, test_ids_fp)
    print(f"Testing IDs saved to {test_ids_fp}")


def list_to_file(data, file_path) -> None:
    with open(file_path, 'w') as file:
        for item in data:
            file.write(f"{item}\n")


def get_args() -> Namespace:
    description = "A utility script to create random splits for the CASS dataset"
    parser = ArgumentParser(
        description=description, formatter_class=ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--cleaned-files-dir",
        default="./cleaned_files/",
        help="path to cleaned files directory",
    )
    parser.add_argument(
        "--data-split-dir",
        default="./data_split_20220417/",
        help="path to data splits directory",
    )
    parser.add_argument(
        "--train-size",
        default=0.8,
        type=float,
        help="the proportion of the dataset to include in the train split",
    )
    parser.add_argument(
        "--val-size",
        default=0.1,
        type=float,
        help="the proportion of the dataset to include in the validation split",
    )
    parser.add_argument(
        "--test-size",
        default=0.1,
        type=float,
        help="the proportion of the dataset to include in the test split",
    )
    parser.add_argument("--seed", default=42, type=int, help="random seed")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    main()
