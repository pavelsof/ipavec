import operator
import pickle
import warnings

from ipatok.ipa import is_letter, is_tie_bar

from keras.layers import Dense, Embedding, Flatten, Input
from keras.models import Model
from keras.utils import to_categorical



"""
Default path where to store to and load from the trained embeddings/vector
representations of IPA tokens.
"""
DEFAULT_MODEL_PATH = 'models/neural_net'


"""
Mapping from IPA tokens to their respective vector representations obtained in
train(); inited in load() and used in get_vector() and calc_delta().
"""
VECTORS = None



def normalise_token(token):
	"""
	Remove tie bars (e.g. t͡ʃ → tʃ) and diacritics marking non-syllabic vowels
	(e.g. aɪ̯ → aɪ) from a token. This ensures a single (arbitrarily chosen)
	"normal" form of tokens with such symbols.
	"""
	return ''.join([char for char in token
					if not is_tie_bar(char) and char != '◌̯'[1]])



def prepare_training_data(dataset_path):
	"""
	Read a dataset of tokenised IPA strings and return (1) the sorted list of
	all tokens, (2) the list of all tokens, as ints, (3, 4) the lists of the
	preceding and succeeding tokens, as ints. The ints are 0 for non-tokens
	(words' start/end), and positive ints for the ordered tokens.
	"""
	with open(dataset_path, encoding='utf-8') as f:
		words = [[normalise_token(token) for token in line.strip().split()]
				for line in f]

	tokens = sorted(set([token for word in words for token in word]))
	assert '<' not in tokens and '>' not in tokens

	tokens_to_ix = {token: index+1 for index, token in enumerate(tokens)}
	tokens_to_ix['<'], tokens_to_ix['>'] = 0, 0

	inputs, outputs_left, outputs_right = [], [], []

	for count, word in enumerate(words):
		for index, token in enumerate(word):
			token_left = word[index-1] if index > 0 else '<'
			token_right = word[index+1] if index < len(word)-1 else '>'

			outputs_left.append(tokens_to_ix[token_left])
			inputs.append(tokens_to_ix[token])
			outputs_right.append(tokens_to_ix[token_right])

	return tokens, inputs, outputs_left, outputs_right



def make_model(vocab_size):
	"""
	Create and compile (but do not train) a Keras model that can be trained to
	predict IPA tokens' left and right neighbours. The vocab_size arg should be
	the total number of distinct tokens, including the non-token (0).
	"""
	main_input = Input(shape=(1,))
	x = Embedding(
			input_dim=vocab_size, output_dim=64, input_length=1,
			name='embedding')(main_input)
	x = Flatten()(x)
	x = Dense(
			128, kernel_initializer='he_uniform',
			activation='relu', name='dense_common')(x)

	out_left = Dense(
					vocab_size, activation='softmax', name='left')(x)
	out_right = Dense(
					vocab_size, activation='softmax', name='right')(x)

	model = Model(inputs=[main_input], outputs=[out_left, out_right])
	model.compile(
			optimizer='sgd',
			loss='categorical_crossentropy',
			metrics=['accuracy'])

	return model



def train(dataset_path, output_path=DEFAULT_MODEL_PATH):
	"""
	Train IPA token embeddings on a dataset and pickle the obtained vector
	representations.
	"""
	tokens, x, y_left, y_right = prepare_training_data(dataset_path)
	vocab_size = len(tokens) + 1

	y_left = to_categorical(y_left, num_classes=vocab_size)
	y_right = to_categorical(y_right, num_classes=vocab_size)

	model = make_model(vocab_size)
	model.fit(x, [y_left, y_right], epochs=5, batch_size=235)

	weights = model.get_layer('embedding').get_weights()[0]

	vectors = {token: weights[index+1] for index, token in enumerate(tokens)}
	vectors[''] = weights[0]

	with open(output_path, 'wb') as f:
		pickle.dump(vectors, f, protocol=3)



def load(model_path=DEFAULT_MODEL_PATH):
	"""
	Load a model; this should be a pickled dict mapping IPA tokens to vector
	representations.
	"""
	global VECTORS

	with open(model_path, 'rb') as f:
		VECTORS = pickle.load(f)



def get_vector(token):
	"""
	Return the vector representation (an entry from VECTORS) of an IPA token.
	Raise an exception if VECTORS is not yet set.
	"""
	token = normalise_token(token)

	try:
		return VECTORS[token]
	except KeyError:
		pass

	alt_token = ''.join([char for char in token if is_letter(char, False)])

	try:
		return VECTORS[alt_token]
	except KeyError:
		warnings.warn('neural-net: cannot recognise {}'.format(token))
		return VECTORS['']



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes/IPA tokens, i.e. the cosine
	distance between their vector representations.
	"""
	return - sum(map(operator.mul, get_vector(phon_a), get_vector(phon_b)))
