def calc_delta(phon_a, phon_b):
	"""
	Calculate the delta between two phonemes.
	"""
	if phon_a == '' or phon_b == '' or phon_a != phon_b:
		return 1
	else:
		return -1
