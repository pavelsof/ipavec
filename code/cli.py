import argparse
import csv

from code.data import (
		DatasetError, WordsDataset, AlignmentsDataset, write_alignments)
from code.main import main



def validate_columns(string):
	"""
	Raise an ArgumentTypeError if the argument is not a comma-separated list of
	strings, suitable for being a columns arg for the Dataset class.

	Helper for Cli's ArgumentParser instance.
	"""
	columns = string.split(',')

	if len(columns) != len(WordsDataset.DEFAULT_COLUMNS):
		raise argparse.ArgumentTypeError('{!s} cannot be a valid columns argument')

	return columns


def init_dataset(path, file_format=None, columns=None):
	"""
	Init and return a XyzDataset instance to read the dataset specified by the
	path. Raise a DatasetError or a ValueError otherwise.

	Helper for Cli's run method.
	"""
	if file_format is None:
		if path[-4:] not in ['.csv', '.psa', '.tsv']:
			raise ValueError('Could not infer file format: {!s}'.format(path))
		file_format = path[-3:]

	if file_format == 'psa':
		return AlignmentsDataset(path)
	else:
		dialect = csv.excel_tab if file_format == 'tsv' else csv.excel
		return WordsDataset(path, dialect, columns)



class Cli:
	"""
	Handles the user input, invokes the necessary functions, and takes care of
	exiting the programme.

	Usage:
		if __name__ == '__main__':
			cli = Cli()
			cli.run()
	"""

	def __init__(self):
		"""
		Setup the argparse parser.
		"""
		self.parser = argparse.ArgumentParser(add_help=False)
		self.parser.add_argument('dataset', help='path to the dataset file')

		io_args = self.parser.add_argument_group('optional arguments - input/output')
		io_args.add_argument(
			'--format',
			choices=['csv', 'psa', 'tsv'],
			help=(
				'the file format to use for reading the dataset; '
				'the default is to use the file extension'))
		io_args.add_argument(
			'--columns',
			default=','.join(WordsDataset.DEFAULT_COLUMNS),
			type=validate_columns,
			help=(
				'comma-separated list comprising the column headings for '
				'the language, concept and transcription columns, respectively; '
				'only relevant if the format is csv/tsv'))
		io_args.add_argument(
			'--output',
			help=(
				'path where to write the output, in psa format; '
				'the default is to write to stdout'))

		other_args = self.parser.add_argument_group('optional arguments - other')
		other_args.add_argument(
			'-h', '--help',
			action='help',
			help='show this help message and exit')


	def run(self, raw_args=None):
		"""
		Parse the given args (if these are None, default to parsing sys.argv,
		which is what you would want unless you are unit testing).
		"""
		args = self.parser.parse_args(raw_args)

		try:
			dataset = init_dataset(args.dataset, args.format, args.columns)
		except (DatasetError, ValueError) as err:
			self.parser.error(str(err))

		write_alignments(main(dataset), args.output)
