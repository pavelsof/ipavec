import importlib



MODULES = ['one-hot', 'phoible', 'phoible-pc']



def list_providers():
	"""
	Return the list of possible providers of delta functions.
	"""
	return sorted(MODULES)


def get_delta_func(module_id):
	"""
	Return the given module's delta function.
	"""
	module_id = module_id.replace('-', '_')
	module = importlib.import_module('code.phon.{}'.format(module_id))
	return module.calc_delta
