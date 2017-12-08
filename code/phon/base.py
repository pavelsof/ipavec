from ipatok import tokenise



def get_inventory(words):
	"""
	Return the phoneme inventory of, i.e. the set of phonemes found in, the
	given collection of words (data.Word tuples).
	"""
	return set([token for word in words for token in tokenise(word.trans, replace=True)])



class DeltaCalc:
	"""
	"""

	def __init__(self, inventory_a, inventory_b):
		"""
		"""
		pass


	def calc_delta(self, phon_a, phon_b):
		"""
		Return the delta between two phonemes.
		"""
		pass
