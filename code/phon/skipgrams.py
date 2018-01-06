import os.path
import warnings

from gensim.models import Word2Vec



"""
Path to a trained word2vec skipgram model.
"""
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'skipgrams')

model = Word2Vec.load(MODEL_PATH)



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the distance between their
	skipgram embeddings.
	"""
	if phon_a not in model.wv:
		warnings.warn('skipgrams: cannot recognise {}'.format(phon_a))
		phon_a = '\0'

	if phon_b not in model.wv:
		warnings.warn('skipgrams: cannot recognise {}'.format(phon_b))
		phon_b = '\0'

	return model.wv.distance(phon_a, phon_b)
