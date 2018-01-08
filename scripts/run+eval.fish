#!/usr/bin/fish

begin
	set -x PYTHONHASHSEED 42

	# helper that parses run.py's help info to extract arg choices
	function get_choices
		set -l IFS ','
		set -l output_arr
		python run.py --help \
			| grep "^  --$argv[1]" \
			| grep -o '{.*}' \
			| tr -d '{}' \
			| read -a output_arr
		echo $output_arr
	end

	# set $usage, $align_choices, and $vectors_choices
	set -l usage "usage: run+eval.fish dataset [align] [vectors]"
	get_choices 'align' | read -al align_choices
	get_choices 'vectors' | read -al vectors_choices

	# ensure the right number of args
	if test (count $argv) -eq 0
		echo $usage; exit 1
	else if test (count $argv) -ge 4
		echo $usage; exit 1
	end

	# parse args
	set -l dataset $argv[1]

	if test (count $argv) -eq 2
		if contains $argv[2] $align_choices
			set align_choices {$argv[2]}
		else
			set vectors_choices {$argv[2]}
		end
	else if test (count $argv) -eq 3
		set align_choices {$argv[2]}
		set vectors_choices {$argv[3]}
	end

	# output dir
	set -l output_dir "output/"(basename $dataset | cut -d '.' -f 1)
	mkdir -p $output_dir

	# run and eval
	for align_arg in $align_choices
		for vectors_arg in $vectors_choices
			set -l output "$output_dir/$align_arg-$vectors_arg.psa"

			python run.py $dataset --align $align_arg --vectors $vectors_arg \
			| python eval.py $dataset - --output $output
		end
	end
end
