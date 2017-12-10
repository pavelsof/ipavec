import collections
import csv



Word = collections.namedtuple('Word', 'lang, concept, ipa, cog_class')



class DatasetError(ValueError):
	"""
	Raised when something goes wrong with reading a dataset.
	"""
	pass



class WordsDataset:
	"""
	Handles dataset reading. It is assumed that the dataset would be a csv/tsv
	file that contains at least the columns needed to generate Word tuples.

	Usage:

		try:
			dataset = Dataset(path)
		except DatasetError as err:
			print(err)

		langs = dataset.get_langs()
		langA = dataset.get_lang(langs.pop())
	"""

	DEFAULT_COLUMNS = ('language', 'gloss', 'transcription', 'cognate_class',)


	def __init__(self, path, dialect='excel-tab', columns=DEFAULT_COLUMNS):
		"""
		Init the instance's props, including self.words which comprises the
		relevant data. Raise a DatasetError if the data cannot be loaded.
		"""
		self.path = path
		self.dialect = dialect
		self.columns = columns

		self.words = [word for word in self._read_words()]


	def clean_ipa(self, string):
		"""
		Return (hopefully valid) IPA string out of a transcription field. If
		the latter contains multiple comma-separated entries, only the first
		one is kept. Some common non-IPA symbols are also removed.
		"""
		string = string.strip().split(',')[0].strip()
		string = string.replace('_', ' ')
		return ''.join([char for char in string if char not in '-'])


	def _read_words(self):
		"""
		Generate the [] of Word entries in the dataset. Raise a DatasetError if
		there is a problem reading the file.
		"""
		try:
			with open(self.path, encoding='utf-8', newline='') as f:
				reader = csv.reader(f, dialect=self.dialect)

				header = {value: key for key, value in enumerate(next(reader))}
				for col in self.columns:
					if col not in header:
						raise DatasetError('Could not find column: {}'.format(col))

				ipa_col = header[self.columns[2]]

				for line in reader:
					line[ipa_col] = self.clean_ipa(line[ipa_col])
					yield Word._make([line[header[x]] for x in self.columns])

		except OSError as err:
			raise DatasetError('Could not open file: {}'.format(self.path))

		except csv.Error as err:
			raise DatasetError('Could not read file: {}'.format(self.path))


	def get_langs(self):
		"""
		Return the sorted list of languages found in the dataset.
		"""
		return sorted(set([word.lang for word in self.words]))


	def get_concepts(self):
		"""
		Return the sorted list of concepts found in the dataset.
		"""
		return sorted(set([word.concept for word in self.words]))


	def get_lang(self, lang):
		"""
		Return the list of words (Word named tuples) that belong to the given
		language.
		"""
		return [word for word in self.words if word.lang == lang]



def write_words(words, path, dialect='excel-tab', header=WordsDataset.DEFAULT_COLUMNS):
	"""
	Write the words (Word tuples) to a csv file with the given dialect. The
	header arg should be a list that contains the headings for the language,
	concept, transcription, and cognate class columns, respectively.
	"""
	with open(path, 'w', encoding='utf-8', newline='') as f:
		writer = csv.writer(f, dialect=dialect)
		writer.writerow(header)

		for word in words:
			writer.writerow(word)



class AlignmentsDataset:
	"""
	"""

	def __init__(self):
		pass



def write_alignments(alignments, path):
	"""
	"""
	pass
