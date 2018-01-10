# bdpa datasets

This directory contains the pairwise alignment datasets from the [Benchmark
Database for Phonetic Alignment][1].

* `covington`: Covington's (1996) original benchmark, in IPA;
* `global`: BDPA's master dataset;
* `tone`: BDPA's tonal languages dataset;
* `andean`, `bai`, `bulgarian`, `dutch`, `french`, `germanic`, `japanese`,
  `norwegian`, `ob-ugrian`, `romance`, `sinitic`, `slavic`: the component
  sub-datasets of `global`, obtained using `scripts/partition_bdpa_global.py`.

[1]: http://alignments.lingpy.org/
