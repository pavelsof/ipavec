# northeuralex data

The file `ipa` comprises the IPA transcriptions from the [NorthEuraLex][1]
database, tokenised using [ipatok][2]. The file `word_pairs` contains those word
pairs (tokenised in the same manner) for which the normalised Levenshtein
distance is below 0.5. The NorthEuraLex database itself is not included here
because of its size, but it is freely available; both files were created (and
can be re-created):

```bash
# activate the virtualenv if you have not done so already
source meta/venv/bin/activate

# tokenise all ipa transcriptions from the northeuralex database
scripts/harvest_ipa_tokens.py meta/northeuralex.tsv data/northeuralex/ipa

# tokenise the word pairs for which LDN is below a certain threshold
scripts/harvest_word_pairs.py meta/northeuralex.tsv data/northeuralex/word_pairs
```

[1]: http://northeuralex.org/
[2]: https://pypi.python.org/pypi/ipatok
