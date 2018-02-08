#!/usr/bin/env python

import argparse
import collections
import pickle

import matplotlib.pyplot as plt
import numpy as np

from sklearn.decomposition import PCA



BASIC_TOKENS = collections.OrderedDict({
	'plosives': ['p', 'b', 't', 'd', 'k', 'ɡ'],
	'fricatives': ['f', 'v', 'θ', 'ð', 's', 'z', 'ʃ', 'ʒ'],
	'vowels': ['i', 'y', 'u', 'ɯ', 'e', 'ø', 'ɤ', 'o', 'ə', 'ɛ', 'ʌ', 'ɔ'],
	'all': [
		'p', 'b', 't', 'd', 'k', 'ɡ',
		'f', 'v', 's', 'z',
		'i', 'u', 'e', 'o', 'ə', 'ɛ', 'ɔ', 'a']
})



def plot(model_path, tokens):
	"""
	Apply PCA on IPA token embeddings and plot the 2d vectors of a subset of
	the tokens. The model should be a pickled {token: embedding} dict.
	"""
	with open(model_path, 'rb') as f:
		model = pickle.load(f)

	all_tokens = sorted(model.keys())
	all_vectors = np.array([model[token] for token in all_tokens])

	pca = PCA(n_components=2, random_state=42)
	all_vectors = pca.fit_transform(all_vectors)

	print('explained variance: {}'.format(pca.explained_variance_))
	print('tokens to plot: {}'.format(' '.join(tokens)))

	vectors = np.array([
		all_vectors[index] for index, token in enumerate(all_tokens)
		if token in tokens])

	plt.axes().set_aspect('equal')  # force the diagram to be square
	plt.scatter(vectors[:,0], vectors[:,1], marker='.')

	for token, vector in zip(tokens, vectors):
		plt.annotate(' {}'.format(token), vector, fontsize=15)

	plt.show()



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'read a pickled dict mapping IPA tokens to vectors, '
		'pca the vectors to 2 dimensions, and plot a subset of these'))
	parser.add_argument('model', help=(
		'path to the pickled dict, i.e. a trained model'))
	parser.add_argument('subset', choices=BASIC_TOKENS.keys(), help=(
		'the subset to plot'))

	args = parser.parse_args()
	plot(args.model, BASIC_TOKENS[args.subset])
