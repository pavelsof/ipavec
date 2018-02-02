import pickle
import warnings

from ipatok.ipa import is_letter
from ipatok import tokenise

from keras.layers import Dense, Dropout, Embedding, Flatten, Input
from keras.layers import concatenate
from keras.models import Model

import numpy as np

from scipy.spatial.distance import cosine

from code.data import AlignmentsDataset
from code.phon.context import normalise_token



"""
Path to store to and load from the trained embeddings by default.
"""
DEFAULT_MODEL_PATH = 'models/alemb'


"""
Mapping from IPA tokens to their respective vector representations obtained in
train(); inited in load() and used in get_vector() and calc_delta().
"""
VECTORS = None



def prepare_training_data(dataset_path):
	"""
	From a psa dataset extract (1) the sorted list of all tokens; (2) two lists
	of token triplets (previous token, token, next token) as ints; (3) the list
	of 0/1's indicating whether the respective pair of triplets are aligned.

	The False triplets (i.e. the negative samples) are obtained by swapping the
	previous and next tokens for each valid triplet.
	"""
	dataset = AlignmentsDataset(dataset_path)

	tokens = sorted(set([
				token for corr in map(lambda x: x[2].corr, dataset.data)
				for pair in corr for token in pair]))
	assert tokens[0] == ''

	tokens_to_ix = {token: index for index, token in enumerate(tokens)}
	ix_a, ix_b, y = [], [], []

	for corr in map(lambda x: x[2].corr, dataset.data):
		seq_a = [0] + [tokens_to_ix[pair[0]] for pair in corr] + [0]
		seq_b = [0] + [tokens_to_ix[pair[1]] for pair in corr] + [0]

		for i in range(1, len(corr)+1):
			ix_a.extend([
				[seq_a[i-1], seq_a[i], seq_a[i+1]],
				[seq_a[i+1], seq_a[i], seq_a[i-1]]])
			ix_b.extend([
				[seq_b[i-1], seq_b[i], seq_b[i+1]],
				[seq_b[i+1], seq_b[i], seq_b[i-1]]])
			y.extend([True, False])

	return tokens, np.array(ix_a), np.array(ix_b), np.array(y, dtype=np.int_)



def make_model(vocab_size):
	"""
	Create and compile (but do not train) a Keras model that can be trained to
	recognise whether two IPA tokens can be aligned or not. vocab_size refers
	to the total number of distinct IPA tokens, including the non-token (0).
	"""
	embed = Embedding(
			input_dim=vocab_size, output_dim=64, input_length=3,
			name='embedding')

	input_a, input_b = Input(shape=(3,)), Input(shape=(3,))

	x = concatenate([
			Flatten()(embed(input_a)),
			Flatten()(embed(input_b))])

	x = Dense(
			128, kernel_initializer='he_uniform',
			activation='relu', name='dense')(x)
	x = Dropout(0.25, seed=42)(x)

	output = Dense(1, activation='sigmoid', name='out')(x)

	model = Model(inputs=[input_a, input_b], outputs=[output])
	model.compile(
			optimizer='rmsprop',
			loss='binary_crossentropy',
			metrics=['accuracy'])

	return model



def train(dataset_path, output_path=DEFAULT_MODEL_PATH,
			epochs=5, batch_size=32, seed=42):
	"""
	Train IPA token embeddings on a dataset and pickle them.
	"""
	np.random.seed(seed)

	tokens, ix_a, ix_b, y = prepare_training_data(dataset_path)

	model = make_model(len(tokens))
	model.fit([ix_a, ix_b], y, epochs=epochs, batch_size=batch_size)

	weights = model.get_layer('embedding').get_weights()[0]
	vectors = {token: weights[index] for index, token in enumerate(tokens)}

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
			# warnings.warn('alemb: {} → {}'.format(
			# 							token, ' '.join(sub_tokens)))
			sub_vectors = [VECTORS[sub_token] for sub_token in sub_tokens]
			return sum(sub_vectors) / len(sub_vectors)

	try:
		return VECTORS[letters]
	except KeyError:
		warnings.warn('alemb: cannot recognise {}'.format(token))
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
