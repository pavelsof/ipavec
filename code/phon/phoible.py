import collections
import csv
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



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the dot product of their
	PHOIBLE feature vectors.
	"""
	return sum(map(operator.mul, SEGMENTS[phon_a], SEGMENTS[phon_b]))



"""
Load the data
"""
load(DATA_PATH)
