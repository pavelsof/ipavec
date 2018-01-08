import collections
import operator
import warnings

from code.phon import phoible



class LangPair:
	"""
	"""

	def __init__(self, inventory_a, inventory_b):
		"""
		Init the instance's props.
		"""
		self.features = self.get_features(inventory_a) \
						& self.get_features(inventory_b)

		self.Vector = collections.namedtuple('Vector', sorted(self.features))

		phonemes = inventory_a | inventory_b | set([''])

		self.SEGMENTS = {
			phon: self.get_vector(phon) for phon in phonemes}


	def get_features(self, inventory):
		"""
		Return the set of PHOIBLE features (i.e. set of column names) that are
		relevant for the given phoneme inventory (i.e. set of IPA segments).
		"""
		features = set()

		for segment in inventory:
			try:
				vector = phoible.SEGMENTS[segment]
			except KeyError:
				continue

			for feature in vector._fields:
				if getattr(vector, feature) != 0:
					features.add(feature)

		return features


	def get_vector(self, phon):
		"""
		Make a self.Vector tuple for the given phoneme out of the respective
		phoible.SEGMENTS tuple.
		"""
		if phon not in phoible.SEGMENTS:
			phon = ''

		dict_all = phoible.SEGMENTS[phon]._asdict()

		dict_relevant = {key: value
				for key, value in dict_all.items() if key in self.features}

		return self.Vector(**dict_relevant)


	def calc_delta(self, phon_a, phon_b):
		"""
		Calculate the delta between two phonemes.
		"""
		if phon_a in self.SEGMENTS:
			vec_a = self.SEGMENTS[phon_a]
		else:
			warnings.warn('PHOIBLE-SUB: cannot recognise {}'.format(phon_a))
			vec_a = self.SEGMENTS['']

		if phon_b in self.SEGMENTS:
			vec_b = self.SEGMENTS[phon_b]
		else:
			warnings.warn('PHOIBLE-SUB: cannot recognise {}'.format(phon_b))
			vec_b = self.SEGMENTS['']

		return - sum(map(operator.mul, vec_a, vec_b))



def load(path=phoible.DATA_PATH):
	"""
	Make sure that phoible.SEGMENTS is available.
	"""
	phoible.load(path)
