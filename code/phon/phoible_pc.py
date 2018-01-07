import operator
import warnings

from sklearn.decomposition import PCA

from code.phon import phoible



"""
Dict mapping IPA segments to PCA-reduced PHOIBLE feature vectors.
"""
SEGMENTS = {}



def load(n_components=29, random_state=42):
	"""
	Populate the SEGMENTS dict by applying PCA onto phoible.SEGMENTS. Pass the
	args onto the PCA constructor unless.

	Unlike its phoible.load counterpart, this function is not invoked
	automatically when importing the module.
	"""
	try:
		n_components = int(n_components)
		assert n_components > 0
	except (ValueError, AssertionError):
		raise ValueError('phoible-pc: bad value for n_components')

	try:
		random_state = int(random_state)
		assert random_state > 0
	except (ValueError, AssertionError):
		raise ValueError('phoible-pc: bad value for random_state')

	pca = PCA(
			n_components=n_components,
			random_state=random_state)

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
		warnings.warn('phoible-pc: cannot recognise {}'.format(phon_a))
		vec_a = SEGMENTS['']

	if phon_b in SEGMENTS:
		vec_b = SEGMENTS[phon_b]
	else:
		warnings.warn('phoible-pc: cannot recognise {}'.format(phon_b))
		vec_b = SEGMENTS['']

	return - sum(map(operator.mul, vec_a, vec_b))
