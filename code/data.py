import collections
import csv
import itertools



Word = collections.namedtuple('Word', 'lang concept ipa')



class DatasetError(ValueError):
	"""
	Raised when something goes wrong with reading a dataset.
	"""
	pass



class Dataset:
	"""
	Base class that defines the get_* methods used by other modules as well as
	a helper method used by inherited classes.
	"""

	def clean_ipa(self, string):
		"""
		Return (hopefully valid) IPA string out of a transcription field. If
		the latter contains multiple comma-separated entries, only the first
		one is kept. Some common non-IPA symbols are also removed.
		"""
		string = string.strip().split(',')[0].strip()
		string = string.replace('_', ' ')
		return ''.join([char for char in string if char not in '-'])


	def get_langs(self):
		"""
		Return the sorted list of languages found in the dataset. Children
		classes should implement this method.
		"""
		raise NotImplementedError


	def get_word_pairs(self, lang_a, lang_b):
		"""
		Return the list of same-concept Word pairs of two languages. Children
		classes should implement this method.
		"""
		raise NotImplementedError



class WordsDataset(Dataset):
	"""
	Handles reading csv/tsv datasets. It is assumed that such a dataset would
	contain at least the columns needed to generate Word tuples.

	Usage:

		try:
			dataset = WordsDataset(path)
		except DatasetError as err:
			print(err)

		langs = dataset.get_langs()
		langA = dataset.get_lang(langs.pop())
	"""

	DEFAULT_COLUMNS = ('language', 'gloss', 'transcription',)


	def __init__(self, path, dialect='excel-tab', columns=DEFAULT_COLUMNS):
		"""
		Init the instance's props, including self.words which comprises the
		relevant data. Raise a DatasetError if the data cannot be loaded.
		"""
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


	def get_word_pairs(self, lang_a, lang_b):
		"""
		Return the list of same-concept Word pairs of two languages.
		"""
		pairs = []

		words_a = [word for word in self.words if word.lang == lang_a]
		words_b = [word for word in self.words if word.lang == lang_b]

		dict_a = collections.defaultdict(set)
		for word in words_a:
			dict_a[word.concept].add(word)

		dict_b = collections.defaultdict(set)
		for word in words_b:
			dict_b[word.concept].add(word)

		concepts = set(dict_a.keys()) & set(dict_b.keys())
		for concept in concepts:
			pairs.extend(list(itertools.product(dict_a[concept], dict_b[concept])))

		return pairs



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



class AlignmentsDataset(Dataset):
	"""
	Handles reading psa datasets as defined by the Benchmark Database for
	Phonetic Alignments [1].

	Usage:

		try:
			dataset = AlignmentsDataset(path)
		except DatasetError as err:
			print(err)

		langs = dataset.get_langs()
		dataset.get_word_pairs(langs.pop(), langs.pop())

	[1]: http://alignments.lingpy.org/faq.php#formats
	"""

	Alignment = collections.namedtuple('Alignment', 'id corr')


	def __init__(self, path):
		"""
		Init the instance's props, including self.data which comprises the
		relevant data. Raise a DatasetError if the data cannot be loaded.
		"""
		self.path = path
		self.data = collections.OrderedDict()

		for word_a, word_b, alignment in self._read_pairs():
			key = (word_a, word_b) if word_a < word_b else (word_b, word_a)
			self.data[key] = alignment


	def _parse_pair(self, lines):
		"""
		Given a triplet of lines describing an alignment as per the psa spec,
		return the respecitve Word and Alignment named tuples.

		Helper for the _read_pairs method.
		"""
		line_a = lines[1].split()
		line_b = lines[2].split()

		lang_a = line_a[0].strip('.')
		lang_b = line_b[0].strip('.')

		align_a = [token if token != '-' else '' for token in line_a[1:]]
		align_b = [token if token != '-' else '' for token in line_b[1:]]

		ipa_a = self.clean_ipa(''.join(align_a))
		ipa_b = self.clean_ipa(''.join(align_b))

		corr = tuple(zip(align_a, align_b))

		word_a = Word(lang_a, None, ipa_a)
		word_b = Word(lang_b, None, ipa_b)

		return word_a, word_b, self.Alignment(lines[0], corr)


	def _read_pairs(self):
		"""
		Generate the list of Word, Word, Alignment tuples found in the dataset.
		Helper for the __init__ method.
		"""
		try:
			with open(self.path, encoding='utf-8') as f:
				next(f)  # the first line is a dataset identifier

				triplet = []
				for line in map(lambda x: x.strip(), f):
					if line:
						if not line.startswith('#'):
							triplet.append(line)
					else:
						yield self._parse_pair(triplet)
						triplet = []

		except OSError as err:
			raise DatasetError('Could not open file: {}'.format(self.path))

		except IndexError as err:
			raise DatasetError('Could not read file: {}'.format(self.path))


	def get_langs(self):
		"""
		Return the sorted list of languages found in the dataset.
		"""
		langs = set()

		for word_a, word_b in self.data.keys():
			langs.add(word_a.lang)
			langs.add(word_b.lang)

		return sorted(langs)


	def get_word_pairs(self, lang_a, lang_b):
		"""
		Return the list of aligned Word pairs of two languages.
		"""
		if lang_b < lang_a:
			reverse_langs = True
			lang_a, lang_b = lang_b, lang_a
		else:
			reverse_langs = False

		pairs = [(word_a, word_b) for word_a, word_b in self.data.keys()
					if word_a.lang == lang_a and word_b.lang == lang_b]

		if reverse_langs:
			pairs = [(b, a) for a, b in pairs]

		return pairs



def write_alignments(alignments, path, header=''):
	"""
	Write a list of (Word, Word, Alignment) tuples to a psa file.
	"""
	lines = [header]

	for word_a, word_b, alignment in alignments:
		lang_a = '{:.<16}'.format(word_a.lang)[:16]
		lang_b = '{:.<16}'.format(word_b.lang)[:16]

		align_a = [token if token != '' else '-' for token, _ in alignment.corr]
		align_b = [token if token != '' else '-' for _, token in alignment.corr]

		line_a = '\t'.join([lang_a] + align_a)
		line_b = '\t'.join([lang_b] + align_b)

		lines.extend([alignment.id, line_a, line_b, ''])

	with open(path, 'w', encoding='utf-8') as f:
		f.write('\n'.join(lines))
