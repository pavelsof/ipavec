# svmcc datasets

This directory contains the IPA datasets used in the [svmcc paper][1], namely:

| dataset          | families               | source                 |
|------------------|------------------------|------------------------|
| `abvd`           | Austronesian           | Greenhill et al, 2008  |
| `bai`            | Sino-Tibetan           | Wang, 2006             |
| `central_asian`  | Turkic, Indo-European  | Manni et al, 2016      |
| `chinese_1964`   | Sino-Tibetan           | Běijīng Dàxué, 1964    |
| `chinese_2004`   | Sino-Tibetan           | Hóu, 2004              |
| `ielex`          | Indo-European          | Dunn, 2012             |
| `japanese`       | Japonic                | Hattori, 1973          |
| `ob_ugrian`      | Uralic                 | Zhivlov, 2011          |
| `tujia`          | Sino-Tibetan           | Starostin, 2013        |

Each dataset is a .tsv file with the following columns:

| column          | info                                                     |
|-----------------|----------------------------------------------------------|
| `language`      | The word's doculect.                                     |
| `iso_code`      | The ISO 639-3 code of the word's doculect; can be empty. |
| `gloss`         | The word's meaning as described in the dataset.          |
| `global_id`     | The Concepticon ID of the word's gloss.                  |
| `local_id`      | The dataset's ID of the word's gloss.                    |
| `transcription` | The word's transcription in either IPA or ASJP.          |
| `cognate_class` | The ID of the set of cognates the word belongs to.       |
| `tokens`        | The word's phonological segments, space-separated.       |
| `notes`         | Field for additional information; can be empty.          |

The datasets are published under the [Creative Commons Attribution-ShareAlike
4.0 International License][2].

[1]: https://github.com/evolaemp/svmcc
[2]: https://creativecommons.org/licenses/by-sa/4.0/
