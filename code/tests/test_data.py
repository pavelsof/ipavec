import csv
import itertools
import os.path
import string
import tempfile

from unittest import TestCase

from hypothesis.strategies import composite, lists, sets, text
from hypothesis import assume, given

from code.data import Word, Dataset, DatasetError, write_words



@composite
def words(draw):
	words = []

	langs = draw(sets(text(max_size=5), min_size=1))
	concepts = draw(sets(text(max_size=5), min_size=1))

	assume(all(['\0' not in s for s in langs]))
	assume(all(['\0' not in s for s in concepts]))

	num_words = len(langs) * len(concepts)
	trans = draw(lists(text(alphabet=string.ascii_lowercase, max_size=5),
					min_size=num_words, max_size=num_words))

	counter = itertools.count()
	cogs = itertools.cycle(string.digits)

	for lang in langs:
		for concept in concepts:
			words.append(Word._make([
				lang, concept,
				trans[next(counter)], next(cogs) ]))

	return words



class DatasetTestCase(TestCase):

	def test_with_bad_path(self):
		with self.assertRaises(DatasetError) as cm:
			Dataset('')

		self.assertTrue(str(cm.exception).startswith('Could not open file'))

	def test_with_bad_file(self):
		path = os.path.abspath(__file__)

		with self.assertRaises(DatasetError) as cm:
			Dataset(path)

		self.assertTrue(str(cm.exception).startswith('Could not find column'))

	@given(words())
	def test_write_and_get_words(self, words):
		with tempfile.TemporaryDirectory() as temp_dir:
			path = os.path.join(temp_dir, 'dataset.tsv')

			for dialect in csv.list_dialects():
				write_words(words, path, dialect)
				self.assertTrue(os.path.exists(path))

				dataset = Dataset(path, dialect)
				self.assertEqual(dataset.words, words)
