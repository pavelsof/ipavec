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

	MODULES = ['one-hot', 'phoible', 'phoible-pc']


	def __init__(self, module_id, lang_pair_mode=False):
		"""
		Load the necessary code.phon sub-module and init the instance's props.
		"""
		module_id = module_id.replace('-', '_')
		module = importlib.import_module('code.phon.{}'.format(module_id))

		self.cost_func = module.calc_delta


	def get_cost_func(self, inventory_a, inventory_b):
		"""
		Return a function that takes two phonemes (or tuples of phonemes) as
		input and returns the respective cost/delta.
		"""
		return self.cost_func
