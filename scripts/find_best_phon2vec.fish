#!/usr/bin/fish

begin
	set -x PYTHONHASHSEED 42

	set -l dataset $argv[1]

	for size in {5,15,30}
		set -l extra "size=$size"
		echo $extra

		python train.py phon2vec data/northeuralex/ipa --extra $extra

		python run.py $dataset --vectors phon2vec ^ /dev/null \
		| python eval.py $dataset - --output /dev/null

		echo
	end
end
