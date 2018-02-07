import pickle
import warnings

from ipatok.ipa import is_letter
from ipatok import tokenise

from keras.layers import Dense, Embedding, Input, LSTM
from keras.models import Model

import numpy as np

from scipy.spatial.distance import cosine

from code.phon.context import normalise_token



"""
Path to store to and load from the trained embeddings by default.
"""
DEFAULT_MODEL_PATH = 'models/lstm'


"""
Mapping from IPA tokens to their respective vector representations obtained in
train(); inited in load() and used in get_vector() and calc_delta().
"""
VECTORS = None



def prepare_training_data(dataset_path):
	"""
	Read a dataset of pairs of tokenised IPA strings and return (1) the sorted
	list of all tokens, (2, 3) the two columns of the dataset as lists of lists
	of ints. The ints are 0/1 for word start/end and bigger ints for the
	ordered IPA tokens. Word start/end is only indicated in the second list.
	"""
	col_a, col_b = [], []
	with open(dataset_path, encoding='utf-8') as f:
		for line in map(lambda x: x.strip().split('\t'), f):
			col_a.append([normalise_token(token) for token in line[0]])
			col_b.append([normalise_token(token) for token in line[1]])

	tokens = set([token for word in col_a for token in word]) \
			| set([token for word in col_b for token in word])
	tokens = sorted(tokens)
	assert '<' not in tokens and '>' not in tokens

	tokens_to_ix = {token: index+2 for index, token in enumerate(tokens)}
	tokens_to_ix['<'], tokens_to_ix['>'] = 0, 1

	ix_a, ix_b = [], []
	for word_a, word_b in zip(col_a, col_b):
		ix_a.append([tokens_to_ix[token] for token in word_a])
		ix_b.append([0] + [tokens_to_ix[token] for token in word_b] + [1])

	return tokens, ix_a, ix_b



def make_model(vocab_size):
	"""
	Create and compile (but do not train) a sequence-to-sequence Keras model
	that attempts to translate synonymous words across languages. vocab_size
	should be the total number of distinct tokens, including the non-token (0).
	"""
	embed = Embedding(input_dim=vocab_size, output_dim=64, name='embedding')

	encoder_input = Input(shape=(None,))
	encoder = LSTM(256, return_state=True, name='encoder')
	_, state_h, state_c = encoder(embed(encoder_input))

	decoder_input = Input(shape=(None,))
	decoder = LSTM(256, return_sequences=True, name='decoder')
	x = embed(decoder_input)
	x = decoder(x, initial_state=[state_h, state_c])
	output = Dense(vocab_size, activation='softmax')(x)

	model = Model(inputs=[encoder_input, decoder_input], outputs=output)
	model.compile(
			optimizer='rmsprop',
			loss='categorical_crossentropy',
			metrics=['accuracy'])

	return model



def train(dataset_path, output_path=DEFAULT_MODEL_PATH,
											epochs=5, batch_size=32, seed=42):
	"""
	Train IPA token embeddings using an LSTM-powered sequence-to-sequence model
	and pickle the obtained vector representations.
	"""
	np.random.seed(seed)

	tokens, ix_a, ix_b = prepare_training_data(dataset_path)
	y = [word[1:] + [1] for word in ix_b]

	model = make_model(len(tokens))
	model.fit([ix_a, ix_b], y, epochs=epochs, batch_size=batch_size)

	weights = model.get_layer('embedding').get_weights()[0]
	vectors = {token: weights[index+2] for index, token in enumerate(tokens)}

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

	letters = ''.join([char for char in token if is_letter(char, False)])

	if len(letters) > 1:
		sub_tokens = []

		for index, sub_token in enumerate(tokenise(token)):
			if sub_token in VECTORS:
				sub_tokens.append(sub_token)
			elif letters[index] in VECTORS:
				sub_tokens.append(sub_token)
			else:
				break
		else:  # no break
			# warnings.warn('lstm: {} → {}'.format(
			# 							token, ' '.join(sub_tokens)))
			sub_vectors = [VECTORS[sub_token] for sub_token in sub_tokens]
			return sum(sub_vectors) / len(sub_vectors)

	try:
		return VECTORS[letters]
	except KeyError:
		warnings.warn('lstm: cannot recognise {}'.format(token))
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
