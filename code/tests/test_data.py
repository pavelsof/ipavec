import csv
import itertools
import os.path
import string
import tempfile

from unittest import TestCase

from hypothesis.strategies import composite, lists, sets, text
from hypothesis import assume, given

from code.data import (
		Word, DatasetError, WordsDataset, AlignmentsDataset,
		write_words, write_alignments)



@composite
def words(draw):
	words = []

	langs = draw(sets(text(max_size=5), min_size=1))
	concepts = draw(sets(text(max_size=5), min_size=1))

	assume(all(['\0' not in s for s in langs]))
	assume(all(['\0' not in s for s in concepts]))

	num_words = len(langs) * len(concepts)
	ipa = draw(lists(text(alphabet=string.ascii_lowercase, max_size=5),
					min_size=num_words, max_size=num_words))

	counter = itertools.count()

	for lang in langs:
		for concept in concepts:
			words.append(Word._make([lang, concept, tuple(ipa[next(counter)])]))

	return words



class WordsDatasetTestCase(TestCase):

	def test_with_bad_path(self):
		with self.assertRaises(DatasetError) as cm:
			WordsDataset('')

		self.assertTrue(str(cm.exception).startswith('Could not open file'))

	def test_with_bad_file(self):
		path = os.path.abspath(__file__)

		with self.assertRaises(DatasetError) as cm:
			WordsDataset(path)

		self.assertTrue(str(cm.exception).startswith('Could not find column'))

	@given(words())
	def test_write_and_load_words(self, words):
		with tempfile.TemporaryDirectory() as temp_dir:
			path = os.path.join(temp_dir, 'dataset.tsv')

			for dialect in csv.list_dialects():
				write_words(words, path, dialect, tokenised=True)
				self.assertTrue(os.path.exists(path))

				dataset = WordsDataset(path, dialect, is_tokenised=True)
				self.assertEqual(dataset.words, words)



class AlignmentsDatasetTestCase(TestCase):

	def test_with_bad_path(self):
		with self.assertRaises(DatasetError) as cm:
			AlignmentsDataset('')

		self.assertTrue(str(cm.exception).startswith('Could not open file'))

	def test_with_bad_file(self):
		path = os.path.abspath(__file__)

		with self.assertRaises(DatasetError) as cm:
			AlignmentsDataset(path)

		self.assertTrue(str(cm.exception).startswith('Could not read file'))
