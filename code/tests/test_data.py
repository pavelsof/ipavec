import csv
import itertools
import os.path
import string
import tempfile

from unittest import TestCase, skip

from hypothesis.strategies import composite, lists, sets, text
from hypothesis import assume, given

from code.data import (
		Word, Alignment, DatasetError,
		WordsDataset, AlignmentsDataset, write_words)



BASE_DIR = os.path.join(os.path.dirname(__file__), '../..')
TUJIA_DATASET_PATH = os.path.join(BASE_DIR, 'data/svmcc/tujia.tsv')
COVINGTON_DATASET_PATH = os.path.join(BASE_DIR, 'data/bdpa/covington.psa')



@composite
def words(draw):
	words = []

	langs = draw(sets(text(max_size=5), min_size=1))
	concepts = draw(sets(text(max_size=5), min_size=1))

	assume(all(['\0' not in s for s in langs]))
	assume(all(['\0' not in s for s in concepts]))

	num_words = len(langs) * len(concepts)
	alphabet = string.ascii_lowercase.replace('g', '')

	ipa = draw(lists(text(alphabet=alphabet, max_size=5),
					min_size=num_words, max_size=num_words))

	counter = itertools.count()

	for lang in langs:
		for concept in concepts:
			words.append(Word._make([lang, concept, tuple(ipa[next(counter)])]))

	return words



class WordsDatasetTestCase(TestCase):

	def test_with_bad_path(self):
		with self.assertRaises(DatasetError) as cm:
			WordsDataset('here_be_dragons')

		self.assertTrue(str(cm.exception).startswith('Could not open file'))

	def test_with_bad_file(self):
		path = os.path.abspath(__file__)

		with self.assertRaises(DatasetError) as cm:
			WordsDataset(path)

		self.assertTrue(str(cm.exception).startswith('Could not find column'))

	@skip
	def test_with_ob_ugrian(self):
		dataset = WordsDataset(TUJIA_DATASET_PATH)

		self.assertEqual(dataset.get_langs(), [
			'Boluo_Tujia', 'Dianfang_Tujia', 'Duogu_Tujia',
			'Tanxi_Tujia', 'Tasha_Tujia'])

		self.assertEqual(len(dataset.words), 498)
		self.assertEqual(dataset.words[0], Word('Tasha_Tujia', 'I', ('ŋ', 'a', '²⁴')))
		self.assertEqual(dataset.words[-1], Word('Tanxi_Tujia', 'yellow', ('ħ', 'ʉ', '³³')))

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
			AlignmentsDataset('here_be_dragons')

		self.assertTrue(str(cm.exception).startswith('Could not open file'))

	def test_with_bad_file(self):
		path = os.path.abspath(__file__)

		with self.assertRaises(DatasetError) as cm:
			AlignmentsDataset(path)

		self.assertTrue(str(cm.exception).startswith('Could not read file'))

	def test_with_covington(self):
		dataset = AlignmentsDataset(COVINGTON_DATASET_PATH)
		self.assertEqual(dataset.get_langs(), [
			'English', 'Fox', 'French', 'German', 'Iranian', 'Latin',
			'Menomini', 'Old_Greek', 'Sanskrit', 'Spanish'])
		self.assertEqual(len(dataset.data), 82)

		kentum = Word('Latin', None, ('k', 'e', 'n', 't', 'u', 'm'))
		satəm = Word('Iranian', None, ('s', 'a', 't', 'ə', 'm'))

		self.assertEqual(dataset.get_word_pairs('Latin', 'Iranian'), [
			(kentum, satəm)])
		self.assertEqual(dataset.get_alignments('Latin', 'Iranian'), {
			(kentum, satəm): set([Alignment(
				(('k', 's'), ('e', 'a'), ('n', ''), ('t', 't'), ('u', 'ə'), ('m', 'm')),
				'centum/satəm')])})

		self.assertEqual(dataset.get_word_pairs('Iranian', 'Latin'), [
			(satəm, kentum)])
		self.assertEqual(dataset.get_alignments('Iranian', 'Latin'), {
			(satəm, kentum): set([Alignment(
				(('s', 'k'), ('a', 'e'), ('', 'n'), ('t', 't'), ('ə', 'u'), ('m', 'm')),
				'centum/satəm')])})
