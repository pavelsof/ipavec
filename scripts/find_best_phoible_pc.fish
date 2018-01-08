#!/usr/bin/fish

begin
	set -x PYTHONHASHSEED 42

	set -l dataset $argv[1]

	for n_components in (seq 10 30)
		set -l extra "n_components=$n_components"

		python run.py $dataset \
			--vectors phoible-pc \
			--extra $extra \
			^ /dev/null \
		| python eval.py $dataset - --output /dev/null
	end
end
