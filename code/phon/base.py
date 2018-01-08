import importlib



class Phon:
	"""
	Object that provides a common interface for handling IPA representations.

	Basic usage:

		tokens_spa = set([token for word in words['spa'] for token in word.ipa])
		tokens_fra = set([token for word in words['fra'] for token in word.ipa])

		phon = Phon('phoible')
		cost_func = phon.get_cost_func(tokens_spa, tokens_fra)
		print(cost_func('j', 'ʒ'))
	"""

	NON_TRAIN_MODULES = ['one-hot', 'phoible', 'phoible-pc', 'phoible-sub']
	TRAIN_MODULES = ['phon2vec']

	MODULES = NON_TRAIN_MODULES + TRAIN_MODULES


	def __init__(self, module_id, extra_args={}):
		"""
		Import the code.phon module identified by module_id and, if necessary,
		invoke its load() func with the given extra_args.
		"""
		self.module_id = module_id.replace('-', '_')
		self.module = importlib.import_module('code.phon.{}'.format(self.module_id))

		if self.module_id in ['phoible_pc', 'phon2vec']:
			try:
				self.module.load(**extra_args)
			except TypeError:
				raise ValueError('unrecognised extra arguments')


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


	def train(self, dataset_path, output_path=None, extra_args={}):
		"""
		Invoke the imported module's train func with the given args. Raise a
		ValueError if these are not as expected.
		"""
		if output_path is None:
			output_path = self.module.DEFAULT_MODEL_PATH

		try:
			self.module.train(dataset_path, output_path, **extra_args)
		except TypeError:
			raise ValueError('unrecognised extra arguments')
