import collections



"""
Tuple representing a cell in a dynamic programming sequence alignment matrix.
The second element is used for backtracking and should be a frozen set of any
of these strings: . ← ↑ ←↑↑ ←←↑
"""
MatrixCell = collections.namedtuple('MatrixCell', 'cost, back')


"""
Tuple representing an alignment of two sequences, comprising its total cost and
a tuple of the corresponding elements.
"""
Alignment = collections.namedtuple('Alignment', 'delta, corr')



def backtrack(seq_a, seq_b, matrix):
	"""
	Backtrack through an alignment matrix of two sequences. Return the set of
	tuples of corresponding sequence elements.
	"""
	def recurse(x, y):
		if x == 0 and y == 0:
			return [[]]

		res = []

		for pointer in matrix[(x, y)].back:
			if pointer == '←':
				args, corr = (x-1, y), (seq_a[x-1], '')
			elif pointer == '↑':
				args, corr = (x, y-1), ('', seq_b[y-1])
			elif pointer == '.':
				args, corr = (x-1, y-1), (seq_a[x-1], seq_b[y-1])
			elif pointer == '←↑↑':
				args, corr = (x-1, y-2), (seq_a[x-1], tuple(seq_b[y-2:y]))
			elif pointer == '←←↑':
				args, corr = (x-2, y-1), (tuple(seq_a[x-2:x]), seq_b[y-1])

			res.extend([li + [corr] for li in recurse(*args)])

		return res

	return frozenset([
		tuple(li) for li in recurse(len(seq_a), len(seq_b))])



def simple_align(seq_a, seq_b, cost_func):
	"""
	Align two sequences using the standard Needleman-Wunsch algorithm. The last
	arg should be a elem_a, elem_b → float function; it should accept the empty
	string as the value of either of its args, in which case the return value
	can be seen as the respective indel penalty.

	Return the alignments of minimum cost as a frozen set of Alignment tuples.
	"""
	matrix = {}  # (x, y): MatrixCell

	for y in range(len(seq_b) + 1):
		for x in range(len(seq_a) + 1):
			d = collections.defaultdict(set)

			if x > 0:
				cost = matrix[(x-1, y)].cost + cost_func(seq_a[x-1], '')
				d[cost].add('←')

			if y > 0:
				cost = matrix[(x, y-1)].cost + cost_func('', seq_b[y-1])
				d[cost].add('↑')

			if x > 0 and y > 0:
				cost = matrix[(x-1, y-1)].cost + cost_func(seq_a[x-1], seq_b[y-1])
				d[cost].add('.')
			elif x == 0 and y == 0:
				d[0].add('.')

			cost = min(d.keys())
			matrix[(x, y)] = MatrixCell(cost, frozenset(d[cost]))

	return frozenset([
		Alignment(cost, corr) for corr in backtrack(seq_a, seq_b, matrix) ])



def merge_align(seq_a, seq_b, cost_func):
	"""
	Align two sequences using the modified Needleman-Wunsch algorithm that also
	includes merges and splits (horse movements on the matrix).

	In addition to elements and empty strings, the cost func should be able to
	handle tuples of elements as well.

	Return the alignments of minimum cost as a frozen set of Alignment tuples.
	"""
	matrix = {}  # (x, y): MatrixCell

	for y in range(len(seq_b) + 1):
		for x in range(len(seq_a) + 1):
			d = collections.defaultdict(set)

			if x > 0:
				cost = matrix[(x-1, y)].cost + cost_func(seq_a[x-1], '')
				d[cost].add('←')

			if y > 0:
				cost = matrix[(x, y-1)].cost + cost_func('', seq_b[y-1])
				d[cost].add('↑')

			if x > 0 and y > 0:
				cost = matrix[(x-1, y-1)].cost + cost_func(seq_a[x-1], seq_b[y-1])
				d[cost].add('.')
			elif x == 0 and y == 0:
				d[0].add('.')

			if x > 0 and y > 1:
				cost = matrix[(x-1, y-2)].cost + cost_func(seq_a[x-1], seq_b[y-2:y])
				d[cost].add('←↑↑')

			if x > 1 and y > 0:
				cost = matrix[(x-2, y-1)].cost + cost_func(seq_a[x-2:x], seq_b[y-1])
				d[cost].add('←←↑')

			cost = min(d.keys())
			matrix[(x, y)] = MatrixCell(cost, frozenset(d[cost]))

	return frozenset([
		Alignment(cost, corr) for corr in backtrack(seq_a, seq_b, matrix) ])



ALGORITHMS = {
	'standard': simple_align }


def list_algorithms():
	return sorted(ALGORITHMS.keys())


def get_align_func(algo_name):
	return ALGORITHMS[algo_name]
