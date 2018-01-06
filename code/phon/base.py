import importlib



class Phon:
	"""
	Object handling IPA representations. Usage:

		tokens_spa = set([token for word in words['spa'] for token in word.ipa])
		tokens_fra = set([token for word in words['fra'] for token in word.ipa])

		phon = Phon('phoible')
		cost_func = phon.get_cost_func(tokens_spa, tokens_fra)
		print(cost_func('j', 'ʒ'))
	"""

	MODULES = ['one-hot', 'phoible', 'phoible-pc', 'phoible-sub', 'skipgrams']


	def __init__(self, module_id, lang_pair_mode=False):
		"""
		Load the necessary code.phon sub-module and init the instance's props.
		"""
		self.module_id = module_id.replace('-', '_')
		self.module = importlib.import_module('code.phon.{}'.format(self.module_id))


	def get_cost_func(self, inventory_a, inventory_b):
		"""
		Return a function that takes two phonemes (or tuples of phonemes) as
		input and returns the respective cost/delta.
		"""
		if self.module_id == 'phoible_sub':
			pair = self.module.LangPair(inventory_a, inventory_b)
			return pair.calc_delta
		else:
			return self.module.calc_delta
