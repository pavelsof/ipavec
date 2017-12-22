import collections
import itertools
import warnings

from code.data import Alignment



"""
Named tuple for representing evaluation results; includes (1) the incorrect
alignments together with their correct counterparts in the form expected by
data.write_alignments, (2) the number of fully correct predictions, (3) the
number of all predictions, and (4) the score as per Kondrak (2002).
"""
Evaluation = collections.namedtuple(
					'Evaluation', 'mistakes num_correct num_total score')



def evaluate(dataset_true, dataset_pred):
	"""
	Evaluate predicted alignments (dataset_pred) against their gold-standard
	counterparts (dataset_true). Return an Evaluation tuple.

	The latter is expected to contain all word pairs of the former; otherwise,
	a KeyError is raised.
	"""
	total_pred = 0
	correct_pred = 0
	score = 0
	mistakes = []

	for lang_a, lang_b in itertools.combinations(dataset_pred.get_langs(), 2):
		d_pred = dataset_pred.get_alignments(lang_a, lang_b)
		d_true = dataset_true.get_alignments(lang_a, lang_b)

		for (word_a, word_b), al_pred_set in d_pred.items():
			al_true_set = d_true[(word_a, word_b)]
			if len(al_true_set) > 1:
				warnings.warn('More than 1 true alignment for {}:{}'.format(word_a, word_b))
			al_true = al_true_set.pop()

			pair_score = sum([1 if al_pred.corr == al_true.corr else 0
									for al_pred in al_pred_set])
			pair_score /= len(al_pred_set)

			if pair_score == 1:
				correct_pred += 1
			else:
				for al_pred in al_pred_set:
					mistakes.extend([
						(word_a, word_b, Alignment(al_pred.corr, 'predicted')),
						(word_a, word_b, Alignment(al_true.corr, 'correct'))])

			score += pair_score

		total_pred += len(d_pred)

	return Evaluation(mistakes, correct_pred, total_pred, score)
