import collections
import csv
import itertools

from ipatok.ipa import is_letter, is_tie_bar, is_diacritic, is_length, is_tone
from ipatok.ipa import replace_substitutes
from ipatok.tokens import normalise, tokenise, replace_digits_with_chao

from code.utils import open_for_reading, open_for_writing



"""
Named tuple for representing a word, i.e. the tokenised IPA transcription of a
word for a given concept in a given language.

AlignmentsDataset instances expect IPA transcriptions to be already tokenised,
while WordsDataset instances leverage ipatok.
"""
Word = collections.namedtuple('Word', 'lang concept ipa')


"""
Named tuple for representing an alignment between two IPA transcriptions, i.e.
a tuple of corresponding phoneme (IPA token) pair tuples and a comment.

For indels the empty string is used (e.g. ('ɛ', '')).
"""
Alignment = collections.namedtuple('Alignment', 'corr comment')



class DatasetError(ValueError):
	"""
	Raised when something goes wrong with reading a dataset.
	"""
	pass



class Dataset:
	"""
	Base class that defines the get_* methods used by other modules, as well as
	helper method(s) used in children classes.
	"""

	@staticmethod
	def sanitise_token(token, keep_digits=False):
		"""
		Sanitise a string by (1) ensuring its chars' normal form comply to the
		IPA spec; (2) replacing common substitutes with their IPA equivalents;
		(3) excluding chars that are not IPA letters, diacritics, tie bars, or
		length markers.

		If keep_digits is set to True, do not replace digits with Chao letters.

		This method leverages ipatok functions that are not in the package's
		public API.
		"""
		if not keep_digits:
			token = replace_digits_with_chao(token)

		token = replace_substitutes(normalise(token))

		return ''.join([
				char for char in token
				if is_letter(char, strict=False) \
					or is_tie_bar(char) \
					or is_diacritic(char, strict=False) \
					or is_length(char) \
					or is_tone(char, strict=False) or char in '¹²³⁴⁵'])


	def get_langs(self):
		"""
		Return the sorted list of languages found in the dataset. Children
		classes should implement this method.
		"""
		raise NotImplementedError


	def get_words(self, lang):
		"""
		Return the list of Word tuples of a language. Children classes should
		implement this method.
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


	def __init__(self, path, dialect='excel-tab',
					columns=DEFAULT_COLUMNS, is_tokenised=False):
		"""
		Init the instance's props, including self.words, a list of Word tuples
		comprising the relevant data.

		Raise a DatasetError if the data cannot be loaded.
		"""
		self.path = path
		self.dialect = dialect
		self.columns = columns
		self.is_tokenised = is_tokenised

		self.words = [word for word in self._read_words()]


	def _read_ipa(self, string):
		"""
		Process a raw transcription value into a (hopefully valid) tuple of IPA
		tokens. If the former contains multiple comma-separated entries, only
		the first one is kept. Some common non-IPA symbols are also removed.

		If the dataset is advertised as having its IPA data already tokenised,
		then split the string and sanitise the resulting tokens.
		"""
		if self.is_tokenised:
			return tuple([
				self.sanitise_token(token) for token in string.split()])

		string = string.strip().split(',')[0].strip()
		string = replace_digits_with_chao(string)

		return tuple(tokenise(string, replace=True, diphtongs=True))


	def _read_words(self):
		"""
		Generate the [] of Word entries in the dataset. Raise a DatasetError if
		there is a problem reading the file.
		"""
		try:
			with open_for_reading(self.path, newline='') as f:
				reader = csv.reader(f, dialect=self.dialect)

				header = {value: key for key, value in enumerate(next(reader))}
				for col in self.columns:
					if col not in header:
						raise DatasetError('Could not find column: {}'.format(col))

				ipa_col = header[self.columns[2]]

				for line in reader:
					line[ipa_col] = self._read_ipa(line[ipa_col])
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


	def get_words(self, lang):
		"""
		Return the list of Word tuples of a language.
		"""
		return [word for word in self.words if word.lang == lang]


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



def write_words(words, path=None, dialect='excel-tab',
				header=WordsDataset.DEFAULT_COLUMNS, tokenised=False):
	"""
	Write the words ([] of Word tuples) to a csv file using the given dialect.
	If path is None or '-', use stdout.

	The header arg should be a list of the headings for the language, concept,
	and transcription columns, respectively.

	If tokenised is set to True, separate the IPA tokens with spaces.
	"""
	joiner = ' ' if tokenised else ''

	with open_for_writing(path, newline='') as f:
		writer = csv.writer(f, dialect=dialect)
		writer.writerow(header)

		for word in words:
			writer.writerow([word.lang, word.concept, joiner.join(word.ipa)])



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

	def __init__(self, path, keep_digits=False):
		"""
		Init the instance's props, including self.data, a [] of (Word, Word,
		Alignment) tuples (where the first Word is always < the second one).

		Raise a DatasetError if the data cannot be loaded.
		"""
		self.path = path
		self.keep_digits = keep_digits

		self.header = ''
		self.data = []

		for word_a, word_b, alignment in self._read_pairs():
			if word_a < word_b:
				self.data.append((word_a, word_b, alignment))
			else:
				self.data.append((
					word_b, word_a, self._reverse_alignment(alignment)))


	def _reverse_alignment(self, alignment):
		"""
		Produce an Alignment tuple comprising the same alignment but with the
		correspondence pairs reversed; i.e. convert an alignment between langs
		A and B into an alignment between langs B and A.

		Helper for the __init__ and get_alignments methods.
		"""
		return Alignment(
				tuple([tuple(reversed(corr)) for corr in alignment.corr]),
				alignment.comment)


	def _parse_word(self, line):
		"""
		Parse a .psa line comprising a word, i.e. the second or third line of a
		triplet. Helper for the _parse_pair method.
		"""
		lang, align = line.split('\t', maxsplit=1)
		lang = lang.strip('.')

		align = tuple([
			self.sanitise_token(token, self.keep_digits) if token != '' else ''
			for token in align.split('\t')])

		ipa = tuple([token for token in align if token])

		return Word(lang, None, ipa), align


	def _parse_pair(self, lines):
		"""
		Given a triplet of lines describing an alignment as per the psa spec,
		return the respecitve Word and Alignment named tuples.

		Helper for the _read_pairs method.
		"""
		word_a, align_a = self._parse_word(lines[1])
		word_b, align_b = self._parse_word(lines[2])

		corr = tuple(zip(align_a, align_b))

		return word_a, word_b, Alignment(corr, lines[0])


	def _read_pairs(self):
		"""
		Generate the list of Word, Word, Alignment tuples found in the dataset
		and set self.header. Raise a DatasetError otherwise.

		Helper for the __init__ method.
		"""
		try:
			with open_for_reading(self.path) as f:
				self.header = next(f).strip()  # the dataset identifier

				triplet = []
				for line in map(lambda x: x.strip(), f):
					if line:
						if not line.startswith('#'):
							triplet.append(line)
					else:
						yield self._parse_pair(triplet)
						triplet = []

				if triplet:  # if the file does not end with a blank line
					yield self._parse_pair(triplet)

		except OSError as err:
			raise DatasetError('Could not open file: {}'.format(self.path))

		except (IndexError, ValueError) as err:
			raise DatasetError('Could not read file: {}'.format(self.path))


	def get_langs(self):
		"""
		Return the sorted list of languages found in the dataset.
		"""
		langs = set()

		for word_a, word_b, _ in self.data:
			langs.add(word_a.lang)
			langs.add(word_b.lang)

		return sorted(langs)


	def get_words(self, lang):
		"""
		Return the sorted list of Word tuples of a language.
		"""
		words = []

		for word_a, word_b, _ in self.data:
			if word_a.lang == lang: words.append(word_a)
			if word_b.lang == lang: words.append(word_b)

		return sorted(set(words))


	def get_word_pairs(self, lang_a, lang_b):
		"""
		Return the list of aligned Word pairs of two languages.
		"""
		if lang_b < lang_a:
			reverse_langs = True
			lang_a, lang_b = lang_b, lang_a
		else:
			reverse_langs = False

		pairs = [(word_a, word_b) for word_a, word_b, _ in self.data
					if word_a.lang == lang_a and word_b.lang == lang_b]

		if reverse_langs:
			pairs = [(b, a) for a, b in pairs]

		return pairs


	def get_alignments(self, lang_a, lang_b):
		"""
		Return the {(Word, Word): set of Alignment tuples} dict comprising the
		dataset's alignments for two languages.
		"""
		if lang_b < lang_a:
			reverse_langs = True
			lang_a, lang_b = lang_b, lang_a
		else:
			reverse_langs = False

		res = collections.defaultdict(set)

		for word_a, word_b, alignment in self.data:
			if word_a.lang == lang_a and word_b.lang == lang_b:
				res[(word_a, word_b)].add(alignment)

		if reverse_langs:
			res = {(b, a): set([self._reverse_alignment(x) for x in value])
						for (a, b), value in res.items()}
		else:
			res = dict(res)

		return res



def write_alignments(alignments, path=None, header='OUTPUT'):
	"""
	Write a list of (Word, Word, Alignment) tuples to a psa file. The last
	element of each tuple should be an Alignment named tuple from either this
	or the align module.

	If path is None or '-', use stdout.
	"""
	lines = [header]

	for word_a, word_b, alignment in alignments:
		field_size = str(max(len(word_a.lang), len(word_b.lang)))
		lang_a = ('{:.<'+ field_size +'}').format(word_a.lang)
		lang_b = ('{:.<'+ field_size +'}').format(word_b.lang)

		align_a = [token if token else '-' for token, _ in alignment.corr]
		align_b = [token if token else '-' for _, token in alignment.corr]

		line_a = '\t'.join([lang_a] + align_a)
		line_b = '\t'.join([lang_b] + align_b)

		if hasattr(alignment, 'comment'):
			comment = alignment.comment
		else:
			comment = str(word_a.concept)

		lines.extend([comment, line_a, line_b, ''])

	with open_for_writing(path) as f:
		f.write('\n'.join(lines))
