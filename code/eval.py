import collections
import itertools

from code.data import Alignment



"""
Named tuple for representing evaluation results; includes (1) the incorrect
alignments together with their correct counterparts in the form expected by
data.write_alignments, (2) the number of correct predictions, and (3) of all
predictions.
"""
Evaluation = collections.namedtuple('Evaluation', 'mistakes num_correct num_all')



def evaluate(dataset_true, dataset_pred):
	"""
	Evaluate predicted alignments (dataset_pred) against their gold-standard
	counterparts (dataset_true). Return an Evaluation tuple.

	The latter is expected to contain all word pairs of the former; otherwise,
	a KeyError is raised.
	"""
	total_pred = 0
	mistakes = []

	for lang_a, lang_b in itertools.combinations(dataset_pred.get_langs(), 2):
		d_pred = dataset_pred.get_alignments(lang_a, lang_b)
		d_true = dataset_true.get_alignments(lang_a, lang_b)

		for (word_a, word_b), al_pred in d_pred.items():
			al_true = d_true[(word_a, word_b)]
			if al_pred.corr != al_true.corr:
				mistakes.extend([
					(word_a, word_b, Alignment(al_pred.corr, 'predicted')),
					(word_a, word_b, Alignment(al_true.corr, 'correct'))])

		total_pred += len(d_pred)

	correct_pred = total_pred - int(len(mistakes) / 2)

	return Evaluation(mistakes, correct_pred, total_pred)
