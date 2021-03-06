# ipavec

This is the home of my bachelor thesis, **IPA alignment using vector
representations**, which presents several different methods for obtaining
embeddings of IPA segments in vector space for the purposes of aligning
IPA-encoded sound sequences. The repo contains the code implementation, the
training and evaluation data, and the thesis paper.


## setup

```bash
# clone this repository
git clone https://github.com/pavelsof/ipavec
cd ipavec

# create a python3 virtual environment
python3 -m venv meta/venv
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

# ensure reproducibility of the results
export PYTHONHASHSEED=42

# use train.py to produce embeddings for one of the trainable methods
python train.py --help

# use run.py to run a method on a dataset and output aligned pairs
python run.py --help

# use eval.py to evaluate the output if you have the gold-standard alignments
python eval.py --help
```

### phoible

```bash
python run.py data/bdpa/slavic.psa --vectors phoible --output output/slavic-phoible.psa
python eval.py data/bdpa/slavic.psa output/slavic-phoible.psa | less
```

### phon2vec

```bash
python train.py phon2vec data/northeuralex/ipa --output models/phon2vec
python run.py data/bdpa/slavic.psa --vectors phon2vec --output output/slavic-phon2vec.psa
python eval.py data/bdpa/slavic.psa output/slavic-phon2vec.psa | less
```

### nn+rnn

```bash
python train.py nn data/northeuralex/ipa --extra epochs=10,batch_size=128
python run.py data/bdpa/slavic.psa --vectors nn --output output/slavic-nn.psa
python eval.py data/bdpa/slavic.psa output/slavic-nn.psa | less

python train.py rnn data/northeuralex/word_pairs --extra batch_size=128,from_model=models/nn
python run.py data/bdpa/slavic.psa --vectors rnn --output output/slavic-rnn.psa
python eval.py data/bdpa/slavic.psa output/slavic-rnn.psa | less
```


## evaluation

The table summarises the accuracy achieved by the implemented methods on the
[BDPA datasets][bdpa]. The last two columns list the results of the [PMI][pmi]
and [SCA][sca] methods.

|           | one-hot | phoible | phon2vec | nn      | nn+rnn  |     pmi |     sca |
|-----------|--------:|--------:|---------:|--------:|--------:|--------:|--------:|
| covington |  60.61% |  82.42% |   80.18% |  82.52% |  82.52% |  87.80% |  90.24% |
| andean    |  85.66% |  87.31% |   97.25% |  99.34% |  99.50% |  95.21% |  99.67% |
| bai       |  52.55% |  62.77% |   61.25% |  74.72% |  75.52% |       - |  83.45% |
| bulgarian |  60.54% |  80.54% |   77.98% |  82.55% |  86.70% |  81.70% |  89.34% |
| dutch     |  14.16% |  25.65% |   26.00% |  32.50% |  32.50% |  36.67% |  42.20% |
| french    |  42.94% |  62.92% |   68.94% |  74.30% |  77.04% |  71.98% |  80.90% |
| germanic  |  39.93% |  51.78% |   54.59% |  71.83% |  72.55% |  75.32% |  83.48% |
| japanese  |  53.56% |  65.04% |   73.74% |  62.71% |  71.08% |  68.26% |  82.19% |
| norwegian |  59.39% |  78.87% |   73.69% |  83.53% |  89.06% |  78.11% |  91.77% |
| ob-ugrian |  59.58% |  77.87% |   73.35% |  78.04% |  82.55% |  82.09% |  86.04% |
| romance   |  40.48% |  71.28% |   63.16% |  76.37% |  77.55% |  84.51% |  95.62% |
| sinitic   |  27.34% |  28.57% |   30.75% |  72.46% |  74.04% |       - |  98.95% |
| slavic    |  76.96% |  90.73% |   84.22% |  89.89% |  96.81% |  89.36% |  94.15% |
| global    |  51.83% |  66.64% |   66.99% |  75.88% |  78.45% |       - |  84.84% |


## license

Copyright (C) 2018  Pavel Sofroniev and Çağri Çöltekin

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.


[bdpa]: http://alignments.lingpy.org/
[pmi]: https://doi.org/10.1163/22105832-13030204
[sca]: http://lingulist.de/documents/list-2012-sca.pdf
