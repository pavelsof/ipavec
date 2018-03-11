import collections
import itertools

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
	counterparts (dataset_true). The latter is expected to contain all word
	pairs of the former; otherwise, a KeyError is raised.
	"""
	pairs_total = 0
	pairs_correct = 0
	score = 0
	mistakes = []

	for lang_a, lang_b in itertools.combinations(dataset_pred.get_langs(), 2):
		d_pred = dataset_pred.get_alignments(lang_a, lang_b)
		d_true = dataset_true.get_alignments(lang_a, lang_b)

		for (word_a, word_b), al_pred_set in d_pred.items():
			al_true_set = d_true[(word_a, word_b)]
			al_true_corrs = set([al_true.corr for al_true in al_true_set])

			comment = '{} – {}'.format(''.join(word_a.ipa), ''.join(word_b.ipa))
			pair_score = 0

			for al_pred in al_pred_set:
				if al_pred.corr in al_true_corrs:
					pair_score += 1
				else:
					for al_true in al_true_set:
						mistakes.extend([
							(word_a, word_b, Alignment(
								al_pred.corr, '{}, predicted'.format(comment))),
							(word_a, word_b, Alignment(
								al_true.corr, '{}, correct'.format(comment)))])

			if pair_score == len(al_pred_set):
				pairs_correct += 1

			score += pair_score / len(al_pred_set)
			pairs_total += 1

	return Evaluation(mistakes, pairs_correct, pairs_total, score)
