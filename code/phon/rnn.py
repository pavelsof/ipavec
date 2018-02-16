import os
import pickle
import random
import warnings

from ipatok.ipa import is_letter
from ipatok import tokenise

from keras.callbacks import TensorBoard
from keras.layers import Dense, Embedding, Input, SimpleRNN
from keras.models import Model
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical

import numpy as np

from scipy.spatial.distance import cosine

import tensorflow

from code.phon.nn import normalise_token



"""
Path to store to and load from the trained embeddings by default.
"""
DEFAULT_MODEL_PATH = 'models/rnn'


"""
Mapping from IPA tokens to their respective vector representations obtained in
train(); inited in load() and used in get_vector() and calc_delta().
"""
VECTORS = None



def prepare_training_data(dataset_path):
	"""
	Read a dataset of pairs of tokenised IPA strings and return (1) the sorted
	list of all tokens, (2, 3) the two columns of the dataset as lists of lists
	of ints (with 0, 1, and 2 reserved for padding and word start/end, token
	indices start from 3).
	"""
	col_a, col_b = [], []
	with open(dataset_path, encoding='utf-8') as f:
		for line in map(lambda x: x.strip().split('\t'), f):
			col_a.append([normalise_token(token) for token in line[0].split()])
			col_b.append([normalise_token(token) for token in line[1].split()])

	tokens = set([token for word in col_a for token in word]) \
			| set([token for word in col_b for token in word])
	tokens = sorted(tokens)

	tokens_to_ix = {token: index+3 for index, token in enumerate(tokens)}

	ix_a, ix_b = [], []
	for word_a, word_b in zip(col_a, col_b):
		ix_a.append([tokens_to_ix[token] for token in word_a])
		ix_b.append([tokens_to_ix[token] for token in word_b])

	return tokens, ix_a, ix_b



def prepare_initial_weights(model_path, tokens):
	"""
	Prepare initial weights for RNN model embedding layer. model_path should
	point to a pickled dict mapping IPA tokens to vectors (usually the output
	of training a context model). tokens should comprise the vocabulary being
	embedded.

	The first three rows of the returned matrix are zeroes, reserved for the
	padding and word boundaries non-tokens.
	"""
	weights = np.zeros((len(tokens)+3, 64))

	with open(model_path, 'rb') as f:
		model = pickle.load(f)

	for index, token in enumerate(tokens, 3):
		if token in model:
			weights[index] = model[token]

	return weights



def make_model(vocab_size, initial_weights=None):
	"""
	Create and compile (but do not train) a sequence-to-sequence Keras model
	that attempts to translate synonymous words across languages. vocab_size
	should be the total number of distinct tokens, including for padding (0)
	and word start (1) and end (2). The second arg allows setting the initial
	weights of the embedding layer.
	"""
	if initial_weights is not None:
		embed = Embedding(
					input_dim=vocab_size, output_dim=64, mask_zero=True,
					weights=[initial_weights], name='embedding')
	else:
		embed = Embedding(
					input_dim=vocab_size, output_dim=64, mask_zero=True,
					name='embedding')

	encoder_input = Input(shape=(None,), name='encoder_input')
	encoder = SimpleRNN(128, return_state=True, name='encoder')
	_, state = encoder(embed(encoder_input))

	decoder_input = Input(shape=(None,), name='decoder_input')
	decoder = SimpleRNN(128, return_sequences=True, name='decoder')
	x = embed(decoder_input)
	x = decoder(x, initial_state=state)
	output = Dense(vocab_size, activation='softmax', name='dense')(x)

	model = Model(inputs=[encoder_input, decoder_input], outputs=output)
	model.compile(
			optimizer='rmsprop',
			loss='categorical_crossentropy',
			metrics=['accuracy'])

	return model



def make_callbacks(tokens, tensorboard_dir):
	"""
	Init and return (in a list) a TensorBoard Keras callback instance to be
	used for visualising the token embeddings.
	"""
	try:
		os.makedirs(tensorboard_dir, exist_ok=True)
	except OSError as err:
		raise ValueError('tensorboard_dir is not writable: {!s}'.format(err))

	metadata_path = os.path.join(tensorboard_dir, 'metadata')

	with open(metadata_path, 'w', encoding='utf-8') as f:
		f.write('\n'.join(['<MASK>', '<START>', '<END>'] + tokens))

	tensorboard = TensorBoard(
					log_dir=tensorboard_dir,
					write_images=True,
					embeddings_freq=1,
					embeddings_layer_names=['embedding'],
					embeddings_metadata='metadata')

	return [tensorboard]



def train(dataset_path, output_path=DEFAULT_MODEL_PATH, from_model=None,
					tensorboard_dir=None, epochs=5, batch_size=32, seed=42):
	"""
	Train IPA token embeddings using an RNN-powered sequence-to-sequence model
	and pickle the obtained vector representations.
	"""
	random.seed(seed)
	np.random.seed(seed)
	tensorflow.set_random_seed(seed)

	tokens, ix_a, ix_b = prepare_training_data(dataset_path)
	vocab_size = len(tokens) + 3

	encoder_x = pad_sequences(ix_a, padding='post')
	decoder_x = pad_sequences([[1] + row for row in ix_b], padding='post')
	decoder_y = pad_sequences(
					[to_categorical(row + [2], vocab_size) for row in ix_b],
					padding='post')

	if from_model:
		initial_weights = prepare_initial_weights(from_model, tokens)
	else:
		initial_weights = None

	if tensorboard_dir is None:
		tensorboard_dir = 'meta/board-rnn-{!s}-{!s}'.format(epochs, batch_size)

	callbacks = make_callbacks(tokens, tensorboard_dir)

	model = make_model(vocab_size, initial_weights)
	model.fit(
			[encoder_x, decoder_x], decoder_y,
			epochs=epochs, batch_size=batch_size, callbacks=callbacks)

	weights = model.get_layer('embedding').get_weights()[0]
	vectors = {token: weights[index+3] for index, token in enumerate(tokens)}

	if from_model:
		with open(from_model, 'rb') as f:
			base_vectors = pickle.load(f)

		for token, vector in base_vectors.items():
			if token not in vectors:
				vectors[token] = vector

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
			# warnings.warn('rnn: {} → {}'.format(
			# 							token, ' '.join(sub_tokens)))
			sub_vectors = [VECTORS[sub_token] for sub_token in sub_tokens]
			return sum(sub_vectors) / len(sub_vectors)

	try:
		return VECTORS[letters]
	except KeyError:
		warnings.warn('rnn: cannot recognise {}'.format(token))
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
