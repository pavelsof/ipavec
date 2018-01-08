#!/usr/bin/env python

import argparse
import csv

from ipatok import tokenise



def read_column(path, dialect, column):
	"""
	Return a column from a csv/tsv dataset (the dialect arg is passed on to
	csv.reader) as a [] of strings.
	"""
	with open(path, encoding='utf-8', newline='') as f:
		reader = csv.DictReader(f, dialect=dialect)
		data = [row[column] for row in reader]

	return data


def write_tokens(path, tokenised_data):
	"""
	Write a [] of tokenised transcriptions to a file, one transcription per
	line, with the tokens separated by intervals.
	"""
	with open(path, 'w', encoding='utf-8') as f:
		f.write('\n'.join([
			' '.join(tokens)
			for tokens in tokenised_data]))


def tokenise_ipa(ipa_data):
	"""
	Tokenise a [] of IPA transcriptions. Remove the hyphens (-) and dots (.)
	before invoking ipatok.
	"""
	res = []

	for trans in ipa_data:
		trans = trans.replace('-', '').replace('.', '')
		trans = tokenise(trans, replace=True, diphtongs=True)
		res.append(trans)

	return res



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(add_help=False, description=(
		'extract the IPA transcriptions from a dataset, '
		'tokenise those, and write them into another file'))

	parser.add_argument(
		'dataset',
		help='path to a dataset with IPA transcriptions in it')
	parser.add_argument(
		'output',
		help='path to write the output to')

	io_args = parser.add_argument_group('optional arguments - input/output')
	io_args.add_argument(
		'-d', '--dialect',
		choices=csv.list_dialects(), default='excel-tab',
		help=(
			'the csv dialect to use for reading the dataset; '
			'the default is excel-tab'))
	io_args.add_argument(
		'-c', '--column',
		default='rawIPA',
		help=(
			'name of the column that contains the IPA data; '
			'the default is rawIPA'))

	other_args = parser.add_argument_group('optional arguments - other')
	other_args.add_argument(
		'-h', '--help',
		action='help',
		help='show this help message and exit')

	args = parser.parse_args()

	data = read_column(args.dataset, args.dialect, args.column)
	data = tokenise_ipa(data)
	write_tokens(args.output, data)
