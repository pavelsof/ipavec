import warnings

from gensim.models import Word2Vec



"""
Default path to store the trained embeddings model to.
"""
DEFAULT_MODEL_PATH = 'data/models/phon2vec'


"""
Trained Word2Vec instance used for calculating distances between phonemes;
inited in load().
"""
model = None



def train(dataset_path, output_path=DEFAULT_MODEL_PATH,
				size=30, window=1, sg=0, negative=1):
	"""
	Train phoneme embeddings using word2vec (with tokenised IPA string being
	the "sentences") on a dataset and store the trained model.
	"""
	with open(dataset_path, encoding='utf-8') as f:
		ipa_data = [line.strip().split() for line in f]

	model = Word2Vec(
				sentences=ipa_data,
				size=size,  # the length of the output vectors
				window=window,  # that many to the left and that many to the right
				min_count=5,  # ignore tokens occurring less often than that
				sg=sg,  # 0 for cbow, 1 for skip-gram
				negative=negative,  # number of negative samples (per positive one?)
				iter=5,  # number of epochs
				null_word=True)  # reached by ['\0']

	model.save(output_path)



def load(model_path=DEFAULT_MODEL_PATH):
	"""
	Load a trained word2vec model into model, the module-level var.
	"""
	global model
	model = Word2Vec.load(model_path)



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the distance between their
	skipgram embeddings.

	If model, the module-level var, is not inited, raise an exception.
	"""
	if phon_a not in model.wv:
		warnings.warn('phon2vec: cannot recognise {}'.format(phon_a))
		phon_a = '\0'

	if phon_b not in model.wv:
		warnings.warn('phon2vec: cannot recognise {}'.format(phon_b))
		phon_b = '\0'

	return model.wv.distance(phon_a, phon_b)
