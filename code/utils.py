import contextlib
import sys



@contextlib.contextmanager
def open_for_reading(path, newline=None):
	"""
	Context manager for reading from either a file or stdin. The newline arg is
	passed on to open() in the former case.

	Usage:

		with open_for_reading('-') as f:
			for line in f:
				do_something(line)
	"""
	if path and path != '-':
		with open(path, encoding='utf-8', newline=newline) as f:
			yield f
	else:
		yield sys.stdin



@contextlib.contextmanager
def open_for_writing(path, newline=None):
	"""
	Context manager for writing to either a file or stdout. The newline arg is
	passed on to open() in the former case.

	Usage:

		with open_for_writing('-') as f:
			f.write('hi')
	"""
	if path and path != '-':
		with open(path, 'w', encoding='utf-8', newline=newline) as f:
			yield f
	else:
		yield sys.stdout
