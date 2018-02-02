import os.path

from unittest import TestCase

from code.phon.alignment import prepare_training_data



BASE_DIR = os.path.join(os.path.dirname(__file__), '../..')
COVINGTON_DATASET_PATH = os.path.join(BASE_DIR, 'data/bdpa/covington.psa')



class PrepareTrainingDataTestCase(TestCase):

	def test_with_covington(self):
		tokens, ix_a, ix_b, y = prepare_training_data(COVINGTON_DATASET_PATH)

		self.assertEqual(tokens, [
			'', 'a', 'ai', 'au', 'aː', 'b', 'bʱ', 'd', 'd͡ʑ', 'e',  # 0-9
			'eː', 'f', 'h', 'i', 'iu', 'iː', 'j', 'k', 'l', 'lː',  # 10-19
			'm', 'n', 'o', 'ou', 'oː', 'p', 'pʰ', 'r', 's', 't',  # 20-29
			'tʰ', 't͡s', 'u', 'uː', 'v', 'w', 'x', 'y', 'z', 'æ',  # 30-39
			'ð', 'ø', 'ŋ', 'ɔː', 'ə', 'ɛ', 'ɛː', 'ɡ', 'ʃ', 'ʒ', 'ʔ', 'θ'])

		self.assertTrue(len(ix_a) == len(ix_b) == len(y))

		self.assertEqual(list(ix_a[0]), [0, 49, 44])
		self.assertEqual(list(ix_a[1]), [44, 49, 0])
		self.assertEqual(list(ix_a[2]), [49, 44, 0])
		self.assertEqual(list(ix_a[3]), [0, 44, 49])

		self.assertEqual(list(ix_b[0]), [0, 16, 22])
		self.assertEqual(list(ix_b[1]), [22, 16, 0])
		self.assertEqual(list(ix_b[2]), [16, 22, 0])
		self.assertEqual(list(ix_b[3]), [0, 22, 16])

		self.assertTrue(all([value == 1
				for index, value in enumerate(y) if index % 2 == 0]))
		self.assertTrue(all([value == 0
				for index, value in enumerate(y) if index % 2 == 1]))
