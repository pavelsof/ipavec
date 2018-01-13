#!/usr/bin/env python

import argparse
import os.path
import sys

from lingpy.align.pairwise import Pairwise

# allow importing modules from ../code
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, parent_dir)

from code.data import AlignmentsDataset
from code.utils import open_for_writing



def run_sca(dataset_path, output_path):
	"""
	Read the word pairs from a psa dataset, align them using the SCA algorithm,
	and write an output psa dataset.
	"""
	dataset = AlignmentsDataset(dataset_path)
	output = ['{} (SCA alignment)'.format(dataset.header)]

	for word_a, word_b, alignment in dataset.data:
		sca = Pairwise(
				word_a.ipa, word_b.ipa,
				merge_vowels=False, merge_geminates=False)
		sca.align()
		align_a, align_b, _ = sca.alignments[0]

		output.extend([
			alignment.comment,
			'\t'.join([word_a.lang] + align_a),
			'\t'.join([word_b.lang] + align_b),
			''])

	with open_for_writing(output_path) as f:
		f.write('\n'.join(output))



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(add_help=False, description=(
		'run List\'s SCA alignment algorithm'))
	parser.add_argument(
		'dataset',
		help='path to a psa dataset to run the SCA algorithm on')

	io_args = parser.add_argument_group('optional arguments - output')
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
	run_sca(args.dataset, args.output)
