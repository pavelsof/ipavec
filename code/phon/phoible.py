import collections
import csv
import itertools
import operator
import os.path



"""
Path to the PHOIBLE IPA features dataset.
"""
DATA_PATH = os.path.join(os.path.dirname(__file__), 'phoible.tsv')


"""
Dict mapping IPA segments to PHOIBLE feature vectors; populated in load().
"""
SEGMENTS = {}


"""
Named tuple representing a PHOIBLE feature vector; inited in load(). Each
element of the tuple is one of these values: -1, 0, 1.
"""
Vector = None



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
			SEGMENTS[line[0]] = Vector._make([d.get(elem, 1) for elem in line[1:]])

	SEGMENTS[None] = Vector._make(itertools.repeat(0, len(Vector._fields)))



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the dot product of their
	PHOIBLE feature vectors.
	"""
	vec_a = SEGMENTS.get(phon_a, SEGMENTS[None])
	vec_b = SEGMENTS.get(phon_b, SEGMENTS[None])

	return - sum(map(operator.mul, vec_a, vec_b))



"""
Load the data
"""
load(DATA_PATH)
