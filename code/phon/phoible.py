import collections
import csv
import itertools
import operator
import os.path
import warnings



"""
Path to the PHOIBLE IPA features dataset.
"""
DATA_PATH = os.path.join(os.path.dirname(__file__), 'phoible.tsv')


"""
Dict mapping IPA segments to PHOIBLE feature vectors; populated in load().
"""
SEGMENTS = collections.OrderedDict()


"""
Named tuple representing a PHOIBLE feature vector; inited in load(). Each
element of the tuple is one of these values: -1, 0, 1.
"""
Vector = None



def canonise(segment):
	"""
	Return the canonical IPA form of a segment. Some PHOIBLE segments do not
	conform strictly to the IPA spec.
	"""
	phoible_to_ipa = {
		'ts': 't͡s', 'tʃ': 't͡ʃ',
		'dz': 'd͡z', 'dʒ': 'd͡ʒ', 'dʑ': 'd͡ʑ',
		'ç': 'ç'}

	for key, value in phoible_to_ipa.items():
		segment = segment.replace(key, value)

	return segment



def load(path):
	"""
	Define the Vector named tuple and populate the SEGMENTS dict. The specified
	file should be like the raw-data/FEATURES/phoible-segments-features.tsv
	dataset found in the phoible/dev repo.
	"""
	global Vector

	d = {'-': -1, '0': 0, '+': 1}

	with open(path, encoding='utf-8', newline='') as f:
		reader = csv.reader(f, delimiter='\t')

		header = next(reader)
		Vector = collections.namedtuple('Vector', header[1:])

		for line in reader:
			SEGMENTS[canonise(line[0])] = \
					Vector._make([d.get(elem, 1) for elem in line[1:]])

	SEGMENTS[''] = Vector._make(itertools.repeat(0, len(Vector._fields)))



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
load(DATA_PATH)
