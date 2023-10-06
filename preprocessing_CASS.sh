#!/bin/bash
#SBATCH --job-name=preprocessing_CASS
#SBATCH --mail-type=ALL
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --partition=main-cpu

module --quiet load anaconda/3
conda activate cass
python preprocessing_CASS.py --data_dir cass