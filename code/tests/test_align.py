from unittest import TestCase

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
