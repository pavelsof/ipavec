import pickle
import warnings

from ipatok.ipa import is_letter, is_tie_bar

from keras.layers import Dense, Embedding, Flatten, Input
from keras.models import Model

import numpy as np

from scipy.spatial.distance import cosine



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



def prepare_training_data(dataset_path, large_context=False):
	"""
	Read a dataset of tokenised IPA strings and return (1) the sorted list of
	all tokens, (2) the list of all tokens, as ints, (3, 4) the lists of the
	preceding and succeeding tokens, as ints. The ints are 0 for non-tokens
	(words' start/end), and positive ints for the ordered tokens.

	If the large_context flag is set, also return the lists for the tokens at
	distance two.
	"""
	with open(dataset_path, encoding='utf-8') as f:
		words = [[normalise_token(token) for token in line.strip().split()]
				for line in f]

	tokens = sorted(set([token for word in words for token in word]))
	assert '<' not in tokens and '>' not in tokens

	tokens_to_ix = {token: index+1 for index, token in enumerate(tokens)}
	tokens_to_ix['<'], tokens_to_ix['>'] = 0, 0

	ix, ix_prev, ix_next = [], [], []
	if large_context:
		ix_prev2, ix_next2 = [], []

	for count, word in enumerate(words):
		for index, token in enumerate(word):
			token_prev = word[index-1] if index > 0 else '<'
			token_next = word[index+1] if index < len(word)-1 else '>'

			ix_prev.append(tokens_to_ix[token_prev])
			ix.append(tokens_to_ix[token])
			ix_next.append(tokens_to_ix[token_next])

			if large_context:
				token_prev2 = word[index-2] if index > 1 else '<'
				token_next2 = word[index+2] if index < len(word)-2 else '>'

				ix_prev2.append(tokens_to_ix[token_prev2])
				ix_next2.append(tokens_to_ix[token_next2])

	if large_context:
		return tokens, ix, ix_prev, ix_next, ix_prev2, ix_next2
	else:
		return tokens, ix, ix_prev, ix_next



def make_model(vocab_size, large_context=False):
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

	out_prev = Dense(
					vocab_size, activation='softmax', name='prev')(x)
	out_next = Dense(
					vocab_size, activation='softmax', name='next')(x)
	outputs = [out_prev, out_next]

	if large_context:
		out_prev2 = Dense(
						vocab_size, activation='softmax', name='prev2')(x)
		out_next2 = Dense(
						vocab_size, activation='softmax', name='next2')(x)
		outputs = [out_prev2] + outputs + [out_next2]

	model = Model(inputs=[main_input], outputs=outputs)
	model.compile(
			optimizer='sgd',
			loss='sparse_categorical_crossentropy',
			metrics=['accuracy'])

	return model



def train(dataset_path, output_path=DEFAULT_MODEL_PATH,
			large_context=False, epochs=5, batch_size=32):
	"""
	Train IPA token embeddings on a dataset and pickle the obtained vector
	representations.
	"""
	tokens, x, *y = prepare_training_data(dataset_path, large_context)
	y = [np.array(ix) for ix in y]

	model = make_model(len(tokens)+1, large_context)
	model.fit(
		x, y,
		epochs=epochs, batch_size=batch_size,
		verbose=2 if large_context else 1)

	weights = model.get_layer('embedding').get_weights()[0]

	vectors = {token: weights[index+1] for index, token in enumerate(tokens)}
	vectors[''] = weights[0]

	with open(output_path, 'wb') as f:
		pickle.dump(vectors, f, protocol=3)



def load(model=DEFAULT_MODEL_PATH):
	"""
	Load a model; this should be a pickled dict mapping IPA tokens to vector
	representations.
	"""
	global VECTORS

	with open(model, 'rb') as f:
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
		raise



def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes/IPA tokens, i.e. the cosine
	distance between their vector representations.
	"""
	if phon_a == '' or phon_b == '':
		return 1

	try:
		vec_a, vec_b = get_vector(phon_a), get_vector(phon_b)
	except KeyError:
		return 1

	return cosine(vec_a, vec_b)
