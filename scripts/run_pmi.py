#!/usr/bin/env python

import argparse
import functools
import os.path
import sys

from asjp import ipa2asjp, asjp2ipa

import numpy as np

# allow importing modules from ../code
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, parent_dir)

from code.align import simple_align
from code.data import AlignmentsDataset
from code.utils import open_for_writing



def load_params(params_dir):
	"""
	Load the PMI parameters, a dict mapping tuples of ASJP symbols to their PMI
	scores, and a tuple of gap penalties. Sourced from the svmcc project [1].

	[1] https://github.com/evolaemp/svmcc
	"""
	scores_file = os.path.join(params_dir, 'logodds.csv')
	penalties_file = os.path.join(params_dir, 'gap_penalties.txt')

	# recognised ASJP sound classes
	with open(scores_file) as f:
		sounds = np.array([x.strip('\"')
							for x in f.readline().strip().split(',')])

	# log odds
	with open(scores_file) as f:
		logodds = np.array([x.strip().split(',')[1:]
							for x in f.readlines()[1:]], np.double)

	# convert log odds to dictionary
	scores = dict()
	for i,s1 in enumerate(sounds):
		for j,s2 in enumerate(sounds):
			scores[s1,s2] = logodds[i,j]

	with open(penalties_file) as f:
		penalties = tuple([float(x.strip()) for x in f.readlines()])

	return scores, penalties


def get_align_func(scores, gap_penalties):
	"""
	Construct and return a PMI alignment function that takes two ASJP sequences
	and returns the respective set of Alignment tuples.
	"""
	def cost_func(a, b):
		if a == '': return gap_penalties[0]
		if b == '': return gap_penalties[1]

		if len(a) > 1: a = a[:1]
		if len(b) > 1: b = b[:1]

		return scores[(a, b)]

	return functools.partial(simple_align, cost_func=cost_func)


def run(align_func, dataset_path, output_path):
	"""
	Read the word pairs from a psa dataset, align them using the given func,
	and write an output psa dataset.
	"""
	dataset = AlignmentsDataset(dataset_path)
	output = ['{} (PMI alignment)'.format(dataset.header)]

	for word_a, word_b, alignment in dataset.data:
		asjp_a = ipa2asjp(word_a.ipa)
		asjp_b = ipa2asjp(word_b.ipa)
		alignments = align_func(asjp_a, asjp_b)

	with open_for_writing(output_path) as f:
		f.write('\n'.join(output))



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(add_help=False, description=(
		'run Jäger\'s PMI alignment algorithm on an IPA-encoded psa dataset'))
	parser.add_argument(
		'dataset',
		help='path to a psa dataset to run the PMI algorithm on')

	io_args = parser.add_argument_group('optional arguments - input/output')
	io_args.add_argument(
		'-p', '--params-dir',
		default='data/pmi',
		help=(
			'dir containing the PMI algorithm parameters; '
			'the default is data/pmi'))
	io_args.add_argument(
		'-o', '--output',
		help=(
			'path where to write the output, in psa format; '
			'if omitted or set to - (a hyphen), write to stdout'))

	other_args = parser.add_argument_group('optional arguments - other')
	other_args.add_argument(
		'-h', '--help',
		action='help',
		help='show this help message and exit')

	args = parser.parse_args()

	scores, gap_penalties = load_params(args.params_dir)
	align_func = get_align_func(scores, gap_penalties)

	run(align_func, args.dataset, args.output)
