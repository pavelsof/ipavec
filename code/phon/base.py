import importlib



class Phon:
	"""
	Object that provides a common interface for handling IPA representations.

	Basic usage:

		tokens_spa = set([token for word in words['spa'] for token in word.ipa])
		tokens_fra = set([token for word in words['fra'] for token in word.ipa])

		phon = Phon('phoible')
		phon.load()

		cost_func = phon.get_cost_func(tokens_spa, tokens_fra)
		print(cost_func('j', 'ʒ'))
	"""

	NON_TRAIN_MODULES = ['one-hot', 'phoible', 'phoible-pc', 'phoible-sub']
	TRAIN_MODULES = ['phon2vec']

	MODULES = NON_TRAIN_MODULES + TRAIN_MODULES


	def __init__(self, module_id):
		"""
		Import the code.phon module identified by module_id.
		"""
		self.module_id = module_id.replace('-', '_')
		self.module = importlib.import_module('code.phon.{}'.format(self.module_id))


	def load(self, extra_args={}):
		"""
		Invoke the module's load() func (if it exists) with the given args.
		Most modules must be loaded before their calc_delta func can be used.
		"""
		if hasattr(self.module, 'load'):
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
		if output_path is not None:
			extra_args['output_path'] = output_path

		try:
			self.module.train(dataset_path, **extra_args)
		except TypeError:
			raise ValueError('unrecognised extra arguments')
