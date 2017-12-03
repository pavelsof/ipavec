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

# use run.py to invoke the commands
python run.py --help

# run the code on a dataset
python run.py data/ielex.tsv
```
