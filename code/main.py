import itertools



def collect_inventories(dataset):
	"""
	Return dict mapping the dataset's languages to their respecitve phoneme
	inventories (as a set of IPA tokens).
	"""
	phon_inv = {}

	for lang in dataset.get_langs():
		phon_inv[lang] = set([token
				for word in dataset.get_words(lang)
				for token in word.ipa if token])

	return phon_inv



def main(dataset, align_func, phon):
	"""
	"""
	output = []  # [(Word, Word, Alignment), ..]

	phon_inv = collect_inventories(dataset)

	for lang_a, lang_b in itertools.combinations(dataset.get_langs(), 2):
		word_pairs = dataset.get_word_pairs(lang_a, lang_b)

		cost_func = phon.get_cost_func(phon_inv[lang_a], phon_inv[lang_b])

		for word_a, word_b in word_pairs:
			alignments = align_func(word_a.ipa, word_b.ipa, cost_func)
			output.extend([(word_a, word_b, x) for x in alignments])

	return output
