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
| andean    |  85,66% |  87,31% |     82,31% |   96,12% |     90,25% |
| bulgarian |  60,54% |  80,54% |     78,79% |   77,98% |     74,75% |
| dutch     |  14,16% |  25,65% |     24,53% |   23,10% |     16,00% |
| french    |  42,94% |  62,92% |     61,31% |   63,27% |     50,49% |
| germanic  |  39,93% |  51,84% |     45,98% |   54.45% |     33.71% |
| japanese  |  53.56% |  65.04% |     62.56% |   69.63% |     60.27% |
| norwegian |  59.39% |  78.87% |     75.80% |   73.69% |     51.57% |
| ob-ugrian |  59.58% |  77.87% |     76.20% |   68.92% |     56.04% |
| romance   |  40.48% |  71.28% |     71.04% |   58.59% |     49.16% |
| slavic    |  76.96% |  90.73% |     86.17% |   84.04% |     85.64% |
| global    |  44,76% |  58,28% |     55,82% |   56,32% |     43,91% |

|           |     sca |
|-----------|---------|
| covington |  90,24% |
| andean    |  99,67% |
| bulgarian |  89,34% |
| dutch     |  42,20% |
| french    |  80,90% |
| germanic  |  83,48% |
| japanese  |  82,19% |
| norwegian |  91,77% |
| ob-ugrian |  86,04% |
| romance   |  95,62% |
| slavic    |  94,15% |
