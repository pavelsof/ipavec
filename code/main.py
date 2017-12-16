import itertools

from code.align import simple_align
from code.phon.phoible import calc_delta



def main(dataset):
	"""
	"""
	output = []  # [(Word, Word, Alignment), ..]

	for lang_a, lang_b in itertools.combinations(dataset.get_langs(), 2):
		word_pairs = dataset.get_word_pairs(lang_a, lang_b)

		for word_a, word_b in word_pairs:
			alignments = simple_align(word_a.ipa, word_b.ipa, calc_delta)
			output.append((word_a, word_b, next(iter(alignments))))

	return output
