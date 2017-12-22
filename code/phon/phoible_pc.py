import operator
import warnings

from sklearn.decomposition import PCA

from code.phon import phoible



"""
Dict mapping IPA segments to PCA-reduced PHOIBLE feature vectors.
"""
SEGMENTS = {}



def load():
	"""
	Populate the SEGMENTS dict by applying PCA onto phoible.SEGMENTS.
	"""
	pca = PCA(n_components=18)
	vectors = pca.fit_transform(list(phoible.SEGMENTS.values()))

	for index, key in enumerate(phoible.SEGMENTS.keys()):
		SEGMENTS[key] = list(vectors[index])



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the dot product of their
	PHOIBLE feature vectors.
	"""
	if phon_a in SEGMENTS:
		vec_a = SEGMENTS[phon_a]
	else:
		warnings.warn('PHOIBLE: cannot recognise {}'.format(phon_a))
		vec_a = SEGMENTS['']

	if phon_b in SEGMENTS:
		vec_b = SEGMENTS[phon_b]
	else:
		warnings.warn('PHOIBLE: cannot recognise {}'.format(phon_b))
		vec_b = SEGMENTS['']

	return - sum(map(operator.mul, vec_a, vec_b))



"""
Load the data
"""
load()
