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

|           | one-hot | phoible | phoible-pc | phon2vec | nn      | rnn     |
|-----------|---------|---------|------------|----------|---------|---------|
| covington |  60,61% |  82,42% |     85,37% |   80,18% |  82,52% |  82,52% |
| andean    |  86,47% |  87,93% |     82,91% |   97,52% |  99,32% |  99,49% |
| bai       |  51,89% |  62,21% |      0,23% |   60,90% |  74,34% |  75,15% |
| bulgarian |  60,54% |  80,54% |     78,79% |   77,98% |  82,55% |  86,70% |
| dutch     |  14,16% |  25,65% |     24,53% |   26,00% |  32,50% |  32,50% |
| french    |  42,94% |  62,92% |     61,31% |   68,94% |  74,30% |  77,04% |
| germanic  |  39,82% |  51,81% |     45,98% |   54,51% |  71,78% |  72,50% |
| japanese  |  53,56% |  65,04% |     62,56% |   73,74% |  62,71% |  71,08% |
| norwegian |  59,24% |  78,74% |     75,66% |   73,54% |  83,43% |  88,99% |
| ob-ugrian |  59,58% |  77,87% |     76,20% |   73,35% |  78,04% |  82,55% |
| romance   |  40,48% |  71,28% |     71,04% |   63,16% |  76,37% |  77,55% |
| sinitic   |  27,06% |  28,02% |      0,00% |   30,42% |  70,93% |  72,59% |
| slavic    |  76,96% |  90,73% |     86,17% |   84,22% |  89,89% |  96,81% |
| global    |  51,79% |  66,63% |     55,94% |   66,94% |  75,74% |  78,33% |

|           |     sca |
|-----------|---------|
| covington |  90,24% |
| andean    |  99,66% |
| bai       |  77,64% |
| bulgarian |  89,34% |
| dutch     |  42,20% |
| french    |  80,90% |
| germanic  |  83,45% |
| japanese  |  82,19% |
| norwegian |  91,72% |
| ob-ugrian |  86,04% |
| romance   |  95,62% |
| sinitic   |  61,11% |
| slavic    |  94,15% |
| global    |  83,12% |
