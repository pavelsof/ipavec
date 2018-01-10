#!/usr/bin/env python

import argparse
import collections
import os.path
import re



def read_psa(path):
	"""
	First yield the header and then each triplet (excluding comments) as a
	tuple of stripped lines.
	"""
	with open(path, encoding='utf-8') as f:
		yield next(f).strip()  # the header

		triplet = []
		for line in map(lambda x: x.strip(), f):
			if line:
				if not line.startswith('#'):
					triplet.append(line)
				else:
					yield tuple(triplet)
					triplet = []

		if triplet:  # if the file does not end with a blank line
			yield tuple(triplet)


def write_psa(path, header, triplets):
	"""
	Write a psa dataset file.
	"""
	body = '\n\n'.join([
		'\n'.join(triplet)
		for triplet in triplets])

	with open(path, 'w', encoding='utf-8') as f:
		f.write('\n'.join([header, body]))


def get_source_name(triplet):
	"""
	Given a triplet (as returned by read_psa), determine the name of the
	dataset that the triplet was sourced from.
	"""
	match = re.match('.+\(.+/(.+)\)$', triplet[0])

	if match is None:
		raise ValueError('Could not identify source name: {}'.format(triplet[0]))

	return match.group(1)


def partition(dataset_path, output_dir):
	"""
	Partition a psa dataset (without modifying it) into smaller psa datasets,
	one per source, and write these in a dir.
	"""
	children = collections.defaultdict(list)

	parent = read_psa(dataset_path)
	header = next(parent)

	for triplet in parent:
		children[get_source_name(triplet)].append(triplet)

	for name, triplets in children.items():
		path = os.path.join(output_dir, '{}.psa'.format(name.lower()))
		write_psa(path, '{}: {}'.format(header, name), triplets)
		print('wrote {}'.format(path))



"""
The cli
"""
if __name__ == '__main__':
	parser = argparse.ArgumentParser(description=(
		'partition BDPA\'s global.psa into smaller datasets, '
		'one per source'))
	parser.add_argument('dataset', help=(
		'path to the dataset to partition; '
		'the dataset is not modified'))
	parser.add_argument('output_dir', help=(
		'path to the directory in which to write the partitions'))

	args = parser.parse_args()
	partition(args.dataset, args.output_dir)
