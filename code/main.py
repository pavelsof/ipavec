import collections
import itertools

from code.align import simple_align
from code.phon.base import get_inventory, DeltaCalc



def main(dataset):
	"""
	"""
	all_langs = dataset.get_langs()
	all_concepts = dataset.get_concepts()

	for lang_a, lang_b in itertools.combinations(all_langs, 2):
		words_a = dataset.get_lang(lang_a)
		words_b = dataset.get_lang(lang_b)

		delta_calc = DeltaCalc(get_inventory(words_a), get_inventory(words_b))

		dict_a = collections.defaultdict(set)
		for word in words_a:
			dict_a[word.concept].add(word)

		dict_b = collections.defaultdict(set)
		for word in words_b:
			dict_b[word.concept].add(word)

		concepts = set(dict_a.keys()) & set(dict_b.keys())
		for concept in concepts:
			for word_a, word_b in itertools.product(dict_a[concept], dict_b[concept]):
				simple_align(word_a, word_b)
