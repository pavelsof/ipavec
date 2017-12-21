import argparse
import csv
import sys
import warnings

from code.align import list_algorithms, get_align_func
from code.data import (
		DatasetError, WordsDataset, AlignmentsDataset, write_alignments)
from code.eval import evaluate
from code.main import main
from code.phon import list_providers, get_delta_func



def validate_columns(string):
	"""
	Raise an ArgumentTypeError if the argument is not a comma-separated list of
	strings, suitable for being a columns arg for the Dataset class.

	Helper for RunCli's ArgumentParser instance.
	"""
	columns = string.split(',')

	if len(columns) != len(WordsDataset.DEFAULT_COLUMNS):
		raise argparse.ArgumentTypeError('{!s} cannot be a valid columns argument')

	return columns


def init_dataset(path, file_format=None, columns=None):
	"""
	Init and return a XyzDataset instance to read the dataset specified by the
	path. Raise a DatasetError or a ValueError otherwise.

	Helper for both RunCli and EvalCli's run methods.
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


def print_to_stderr(message, *args, **kwargs):
	"""
	Custom implementation of the default warnings.showwarning func that simply
	prints the warning message to stderr. The default implementation also
	prints meta info (e.g. line number) which is unnecessary for our purposes.

	Relevant docs:
	https://docs.python.org/3/library/warnings.html#warnings.showwarning
	"""
	print(message, file=sys.stderr)



class RunCli:
	"""
	Handles the user input, invokes the necessary functions, and takes care of
	exiting the script for running IPA alignment.

	Usage:
		if __name__ == '__main__':
			cli = RunCli()
			cli.run()
	"""

	def __init__(self):
		"""
		Setup the argparse parser.
		"""
		self.parser = argparse.ArgumentParser(add_help=False)
		self.parser.add_argument(
			'dataset',
			help=(
				'path to the dataset file; '
				'if set to - (a hyphen), read from stdin'))

		algo_args = self.parser.add_argument_group('optional arguments - algorithm')
		algo_args.add_argument(
			'--align',
			choices=list_algorithms(), default='standard',
			help=(
				'which alignment algorithm to use; '
				'the default is the standard Needleman-Wunsch'))
		algo_args.add_argument(
			'--vectors',
			choices=list_providers(), default='phoible',
			help=(
				'which IPA vector representations to use; '
				'the default is PHOIBLE\'s feature vectors'))

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
				'if omitted or set to - (a hyphen), write to stdout'))

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

		align_func = get_align_func(args.align)
		delta_func = get_delta_func(args.vectors)

		alignments = main(dataset, align_func, delta_func)
		header = '{} alignment, {} vectors'.format(args.align, args.vectors)

		write_alignments(alignments, args.output, header)



class EvalCli:
	"""
	Handles the user input, invokes the necessary functions, and takes care of
	exiting the script for evaluating alignments.

	Usage:
		if __name__ == '__main__':
			cli = EvalCli()
			cli.run()
	"""

	def __init__(self):
		"""
		Setup the argparse parser.
		"""
		self.parser = argparse.ArgumentParser(add_help=False)

		self.parser.add_argument(
			'dataset_true',
			help=(
				'path to the dataset with gold-standard alignments; '
				'if set to - (a hyphen), read from stdin'))
		self.parser.add_argument(
			'dataset_pred',
			help=(
				'path to the dataset with predicted alignments; '
				'if set to - (a hyphen), read from stdin; '
				'setting both dataset args to read from stdin does not work'))

		io_args = self.parser.add_argument_group('optional arguments - input/output')
		io_args.add_argument(
			'--output',
			help=(
				'path where to write the output, in psa format; '
				'if omitted or set to - (a hyphen), write to stdout'))

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
			dataset_true = init_dataset(args.dataset_true, 'psa')
			dataset_pred = init_dataset(args.dataset_pred, 'psa')
		except (DatasetError, ValueError) as err:
			self.parser.error(str(err))

		evaluation = evaluate(dataset_true, dataset_pred)
		print('{} → {:.2f}% ({} out of {})'.format(
				dataset_pred.header,
				evaluation.num_correct / evaluation.num_all * 100,
				evaluation.num_correct, evaluation.num_all))

		header = 'evaluation: {}'.format(dataset_pred.header)
		write_alignments(evaluation.mistakes, args.output, header)



"""
Setup the warnings module.
"""
warnings.showwarning = print_to_stderr
