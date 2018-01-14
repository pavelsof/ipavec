import warnings

from gensim.models import Word2Vec
from ipatok.ipa import is_letter, is_tie_bar



"""
Default path to store the trained embeddings model to.
"""
DEFAULT_MODEL_PATH = 'models/phon2vec'


"""
Trained Word2Vec instance used for calculating distances between phonemes;
inited in load().
"""
model = None



def normalise_token(token):
	"""
	Remove tie bars (e.g. t͡ʃ → tʃ) and diacritics marking non-syllabic vowels
	(e.g. aɪ̯ → aɪ) from a token. This ensures a single (arbitrarily chosen)
	"normal" form of tokens with such symbols.
	"""
	return ''.join([char for char in token
					if not is_tie_bar(char) and char != '◌̯'[1]])



def train(dataset_path, output_path=DEFAULT_MODEL_PATH,
				size=15, window=1, seed=42, sg=0, negative=1):
	"""
	Train phoneme embeddings using word2vec (with tokenised IPA string being
	the "sentences") on a dataset and store the trained model.
	"""
	with open(dataset_path, encoding='utf-8') as f:
		ipa_data = [[normalise_token(token) for token in line.strip().split()]
					for line in f]

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



def get_vector_key(token):
	"""
	Return the key that maps to the vector representation of a phoneme (i.e.
	IPA token). Raise an exception if the module-level model is not set.
	"""
	token = normalise_token(token)

	if token in model.wv:
		return token

	if token == '':
		return '\0'

	alt_token = ''.join([char for char in token if is_letter(char, False)])

	if alt_token in model.wv:
		return alt_token

	warnings.warn('phon2vec: cannot recognise {}'.format(token))
	return '\0'



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes, i.e. the distance between their
	skipgram embeddings.

	If model, the module-level var, is not inited, raise an exception.
	"""
	return model.wv.distance(get_vector_key(phon_a), get_vector_key(phon_b))
