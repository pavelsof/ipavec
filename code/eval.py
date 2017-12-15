import itertools

from code.data import Alignment



def evaluate(dataset_true, dataset_pred):
	"""
	Evaluate predicted alignments (dataset_pred) against their gold-standard
	counterparts (dataset_true).

	The latter is expected to contain all word pairs of the former; otherwise,
	a KeyError is raised.

	For the time being this means returning the alignments that differ to be
	written in a new dataset, as well as printing the number of those.
	"""
	total_pred = 0
	output = []  # [(Word, Word, Alignment), (Word, Word, Alignment), ..]

	for lang_a, lang_b in itertools.combinations(dataset_pred.get_langs(), 2):
		d_pred = dataset_pred.get_alignments(lang_a, lang_b)
		d_true = dataset_true.get_alignments(lang_a, lang_b)

		for (word_a, word_b), al_pred in d_pred.items():
			al_true = d_true[(word_a, word_b)]
			if al_pred.corr != al_true.corr:
				output.extend([
					(word_a, word_b, Alignment(al_pred.corr, 'predicted')),
					(word_a, word_b, Alignment(al_true.corr, 'correct'))])

		total_pred += len(d_pred)

	good_ones = total_pred - int(len(output) / 2)
	print('accuracy: {:.2f} ({} out of {})'.format(
			good_ones / total_pred, good_ones, total_pred))

	return output
