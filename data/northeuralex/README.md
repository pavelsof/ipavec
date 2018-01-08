# northeuralex data

The file `ipa` comprises the IPA transcriptions from the [NorthEuraLex][1]
database, tokenised using [ipatok][2]. The database itself is not included here
because of its size, but it is freely available; the file here was created (and
can be re-created) by invoking:

```bash
# activate the virtualenv if you have not done so already
source meta/venv/bin/activate

# tokenise the ipa transcriptions from the northeuralex database
scripts/harvest_ipa_tokens.py ~/downloads/northeuralex-cldf.csv data/northeuralex/ipa
```

[1]: http://northeuralex.org/
[2]: https://pypi.python.org/pypi/ipatok
