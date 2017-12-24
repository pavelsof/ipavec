import itertools



def main(dataset, align_func, phon):
	"""
	"""
	output = []  # [(Word, Word, Alignment), ..]

	for lang_a, lang_b in itertools.combinations(dataset.get_langs(), 2):
		word_pairs = dataset.get_word_pairs(lang_a, lang_b)

		cost_func = phon.get_cost_func(set(), set())

		for word_a, word_b in word_pairs:
			alignments = align_func(word_a.ipa, word_b.ipa, cost_func)
			output.extend([(word_a, word_b, x) for x in alignments])

	return output
