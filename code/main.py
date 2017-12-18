import itertools



def main(dataset, align_func, delta_func):
	"""
	"""
	output = []  # [(Word, Word, Alignment), ..]

	for lang_a, lang_b in itertools.combinations(dataset.get_langs(), 2):
		word_pairs = dataset.get_word_pairs(lang_a, lang_b)

		for word_a, word_b in word_pairs:
			alignments = align_func(word_a.ipa, word_b.ipa, delta_func)
			output.append((word_a, word_b, next(iter(alignments))))

	return output
