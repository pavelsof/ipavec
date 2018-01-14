import warnings

from gensim.models import Word2Vec
from ipatok.ipa import is_letter



"""
Default path to store the trained embeddings model to.
"""
DEFAULT_MODEL_PATH = 'models/phon2vec'


"""
Trained Word2Vec instance used for calculating distances between phonemes;
inited in load().
"""
model = None



def train(dataset_path, output_path=DEFAULT_MODEL_PATH,
				size=15, window=1, seed=42, sg=0, negative=1):
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
				seed=seed,  # random seed
				workers=1,  # needed for reproducibility
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



def clean_phon(phon):
	"""
	If the phoneme is not known to the model, return something that is.
	"""
	if phon in model.wv:
		return phon

	if phon == '':
		return '\0'

	alt = ''.join([char for char in phon if is_letter(char, False)])
	if alt in model.wv:
		return alt

	warnings.warn('phon2vec: cannot recognise {}'.format(phon))
	return '\0'



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the distance between their
	skipgram embeddings.

	If model, the module-level var, is not inited, raise an exception.
	"""
	return model.wv.distance(clean_phon(phon_a), clean_phon(phon_b))
