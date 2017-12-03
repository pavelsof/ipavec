import argparse
import csv

from code.data import DatasetError, Dataset
from code.main import main



def validate_columns(string):
	"""
	Raise an ArgumentTypeError if the argument is not a comma-separated list of
	strings, suitable for being a columns arg for the Dataset class.

	Helper for Cli's ArgumentParser instance.
	"""
	columns = string.split(',')

	if len(columns) != len(Dataset.DEFAULT_COLUMNS):
		raise argparse.ArgumentTypeError('{!s} cannot be a valid columns argument')

	return columns



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
			'--dialect',
			choices=csv.list_dialects(),
			help=(
				'the csv dialect to use for reading the dataset; '
				'the default is to look at the file extension '
				'and use excel for .csv and excel-tab for .tsv'))
		io_args.add_argument(
			'--columns',
			default=','.join(Dataset.DEFAULT_COLUMNS),
			type=validate_columns,
			help=(
				'comma-separated list comprising the column headings for '
				'the language, concept, transcription, and cognate class '
				'columns, respectively'))

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
			dataset = Dataset(args.dataset, args.dialect, args.columns)
		except DatasetError as err:
			self.parser.error(str(err))

		main(dataset)
