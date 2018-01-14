# thesis

Here be a thesis.


## setup

```bash
# clone this repository
git clone $THIS_REPO
cd thesis

# create a python3 virtual environment
virtualenv meta/venv
source meta/venv/bin/activate

# install the dependencies
pip install -r requirements.txt

# check the unit tests
python -m unittest discover code
```


## usage

```bash
# activate the virtual env if it is not already
source meta/venv/bin/activate

# use run.py to run the algorithm on a dataset
python run.py --help

# use eval.py to evaluate the output if you have the gold-standard alignments
python eval.py --help

# use this fish script to directly evaluate with several option combinations
scripts/run+eval.fish data/bdpa/covington.psa
```


## results

|           | one-hot | phoible | phoible-pc | phon2vec | neural-net |
|-----------|---------|---------|------------|----------|------------|
| covington |  60,61% |  82,42% |     85,37% |   80,18% |     75,20% |
| bulgarian |  60,54% |  80,54% |     78,79% |   77,98% |     74,75% |
| global    |  44,76% |  58,28% |     55,82% |   56,32% |     43,91% |

|           |     sca |
|-----------|---------|
| covington |  90,24% |
| bulgarian |  89,34% |
| global    |  72,09% |
