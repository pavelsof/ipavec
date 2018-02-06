#!/usr/bin/env python

import argparse
import itertools
import os.path
import sys

import editdistance

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(1, BASE_DIR)

from code.cli import validate_columns, init_dataset
from code.utils import open_for_writing



def calc_ldn(seq_a, seq_b):
	"""
	Calculate the normalised Levenshtein distance between two sequences.
	"""
	return editdistance.eval(seq_a, seq_b) / max(len(seq_a), len(seq_b))



def harvest_pairs(dataset, threshold):
	"""
	From the dataset, return the IPA transcriptions of those same-meaning word
	pairs the LDN between which is below threshold.
	"""
	pairs = []

	for lang_a, lang_b in itertools.combinations(dataset.get_langs(), 2):
		for word_a, word_b in dataset.get_word_pairs(lang_a, lang_b):
			if calc_ldn(word_a.ipa, word_b.ipa) < threshold:
				pairs.append((word_a.ipa, word_b.ipa))

	return pairs



def write_pairs(path, word_pairs):
	"""
	Write a [] of pairs of IPA sequences to a file, one tab-separated pair per
	line, with the IPA tokens separated by intervals.
	"""
	output = []

	for pair in word_pairs:
		output.append('\t'.join([' '.join(seq) for seq in pair]))

	with open_for_writing(path) as f:
		f.write('\n'.join(output))



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(add_help=False, description=(
		'extract the pairs of IPA-encoded words with the same meaning '
		'from a dataset, tokenise those, and write them into another file'))

	parser.add_argument(
		'dataset',
		help='path to a dataset with IPA-encoded words in it')

	io_args = parser.add_argument_group('optional arguments - input/output')
	io_args.add_argument(
		'--format',
		choices=['csv', 'psa', 'tsv'],
		help=(
			'the file format to use for reading the dataset; '
			'the default is to use the file extension'))
	io_args.add_argument(
		'--columns',
		default=['Language_ID', 'Concept_ID', 'rawIPA'],
		type=validate_columns,
		help=(
			'comma-separated list comprising the column headings for '
			'the language, concept and transcription columns; '
			'the defaults are: Language_ID, Concept_ID, rawIPA'))
	io_args.add_argument(
		'--threshold',
		default=0.5,
		type=float,
		help=(
			'pairs with normalised Levenshtein distance above this value '
			'are omitted; the default is 0.5'))
	io_args.add_argument(
		'--output',
		help=(
			'path to write the output to; '
			'if omitted or set to - (a hyphen), write to stdout'))

	other_args = parser.add_argument_group('optional arguments - other')
	other_args.add_argument(
		'-h', '--help',
		action='help',
		help='show this help message and exit')

	args = parser.parse_args()

	dataset = init_dataset(args.dataset, args.format, args.columns)
	write_pairs(args.output, harvest_pairs(dataset, args.threshold))
