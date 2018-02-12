from unittest import TestCase

import editdistance

from hypothesis.strategies import text
from hypothesis import given

from code.align import Alignment, simple_align, merge_align



class AlignTestCase(TestCase):

	def test_simple_align(self):
		res = simple_align(['з', 'а', 'м', 'б'], ['з', 'ъ', 'б'], lambda a, b: 0 if a == b else 1)
		self.assertEqual(len(res), 2)

		self.assertTrue(Alignment(2, (('з', 'з'), ('а', 'ъ'), ('м', ''), ('б', 'б'))) in res)
		self.assertTrue(Alignment(2, (('з', 'з'), ('а', ''), ('м', 'ъ'), ('б', 'б'))) in res)

		res = simple_align('GCATGCU', 'GATTACA', lambda a, b: -1 if a == b else 1)
		self.assertEqual(len(res), 3)

		self.assertTrue(Alignment(0, (
			('G', 'G'), ('C', ''), ('A', 'A'), ('T', 'T'), ('G', 'T'), ('', 'A'), ('C', 'C'), ('U', 'A')
			)) in res)
		self.assertTrue(Alignment(0, (
			('G', 'G'), ('C', ''), ('A', 'A'), ('', 'T'), ('T', 'T'), ('G', 'A'), ('C', 'C'), ('U', 'A')
			)) in res)
		self.assertTrue(Alignment(0, (
			('G', 'G'), ('C', ''), ('A', 'A'), ('T', 'T'), ('', 'T'), ('G', 'A'), ('C', 'C'), ('U', 'A')
			)) in res)

	def test_merge_align(self):
		res = merge_align(['з', 'а', 'м', 'б'], ['з', 'ъ', 'б'], lambda a, b: 0 if a == b else 1)
		self.assertEqual(len(res), 1)
		self.assertTrue(Alignment(1, (('з', 'з'), (('а', 'м'), 'ъ'), ('б', 'б'))) in res)

	@given(text(max_size=10), text(max_size=10))
	def test_simple_align_distance(self, word_a, word_b):
		res = simple_align(word_a, word_b, lambda a, b: 0 if a == b else 1)
		self.assertEqual(len(set([alignment.delta for alignment in res])), 1)

		delta = list(res)[0].delta
		self.assertEqual(delta, editdistance.eval(word_a, word_b))
