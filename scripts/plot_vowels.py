#!/usr/bin/env python

import argparse
import pickle

import matplotlib.pyplot as plt
import numpy as np

from sklearn.decomposition import PCA



def plot_vowels(model_path):
	"""
	Apply PCA on IPA token embeddings and plot the transformed vowel vectors.
	The path should be to a pickled dict mapping tokens to their embeddings.
	"""
	with open(model_path, 'rb') as f:
		model = pickle.load(f)

	tokens = sorted(model.keys())
	vectors = np.array([model[token] for token in tokens])

	pca = PCA(n_components=2, random_state=42)
	vectors = pca.fit_transform(vectors)

	vowels = ['i', 'y', 'u', 'ɯ', 'e', 'ø', 'ɤ', 'o', 'ə', 'ɛ', 'ʌ', 'ɔ']
	vectors = np.array([
			vectors[i] for i, token in enumerate(tokens) if token in vowels])

	plt.axes().set_aspect('equal')  # force the diagram to be square
	plt.scatter(vectors[:,0], vectors[:,1], marker='.')

	for vowel, vector in zip(vowels, vectors):
		plt.annotate(vowel, vector)

	plt.show()



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'read a pickled dict mapping IPA tokens to vectors, '
		'pca the vectors to 2 dimensions, and plot the vowels'))
	parser.add_argument('model', help=(
		'path to the pickled dict, i.e. a trained model'))

	args = parser.parse_args()
	plot_vowels(args.model)
