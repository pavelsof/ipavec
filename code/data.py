import collections
import csv



Word = collections.namedtuple('Word', 'lang, concept, trans, cog_class')



class DatasetError(ValueError):
	"""
	Raised when something goes wrong with reading a dataset.
	"""
	pass



class Dataset:
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


	def __init__(self, path, dialect=None, columns=DEFAULT_COLUMNS):
		"""
		Init the instance's props, including self.words which comprises the
		relevant data. Raise a DatasetError if the data cannot be loaded.

		The dialect arg should be either a string identifying one of the csv
		dialects or None, in which case the dialect is inferred based on the
		file extension. If the arg is set but not recognised as a valid csv
		dialect, a ValueError is raised.
		"""
		if dialect is None:
			dialect = 'excel-tab' if path.endswith('.tsv') else 'excel'
		elif dialect not in csv.list_dialects():
			raise ValueError('Unrecognised csv dialect: {!s}'.format(dialect))

		self.path = path
		self.dialect = dialect
		self.columns = columns

		self.words = [word for word in self._read_words()]


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

				for line in reader:
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



def write_words(words, path, dialect='excel-tab', header=Dataset.DEFAULT_COLUMNS):
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
