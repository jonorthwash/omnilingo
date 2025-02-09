#!/usr/bin/env python3

import sys
import pathlib
import os 
import json

from tokenisers import tokenise
from taggers import tag
from segments import characters

def deploy(dump_dir, cache_file, static_dir):
	#0	1	2	3				4									5									6
	#8       69      6       common_voice_fi_24001101.mp3    fa032123ba94a9aafc037ca10a5eac754ef410288c8dde2b2c666ed5e10222f2        Mysteerimies oli oppinut moraalinsa taruista, elokuvista ja peleistä.   a8f9eb3f56f2048df119a9ad1d210d0b98fda56f3e2a387f14fe2d652241f3ec

	# Keep track of which audio we've seen (in case there are multiple 
	# files with the same hash) and which text we've seen (we only want
	# two files per transcript
	seen_audio = []
	seen_text = []

	lang_id = cache_file.split('/')[-1]

	index_dir = static_dir + '/index/'
	clips_dir = dump_dir + '/clips/'

	pathlib.Path(index_dir).mkdir(parents=True, exist_ok=True)

	cache_fd = open(cache_file, 'r')
	voc_fd = open(cache_file + '.voc', 'r')
	index_fd = open(index_dir + '/' + lang_id, 'w')

	# Datastructure for the index
	index = {"index": []}

	i = 0
	line = cache_fd.readline()
	while line:
		row = line.strip().split('\t')
		index["index"].append(row)
		fname = row[3]
		ahash = row[4]
		text = row[5]
		thash = row[6]

		if seen_audio.count(ahash) > 0:
			line = cache_fd.readline()
			continue	
		else:
			seen_audio.append(ahash)
			
		if seen_text.count(thash) > 2:
			line = cache_fd.readline()
			continue	
		else:
			seen_text.append(thash)

		tokens = tokenise(row[5], lang=lang_id)
		labels = tag(tokens, lang=lang_id)
		chars = [characters(token, lang=lang_id) for token in tokens]

		audio_dir = static_dir + '/' + lang_id + '/clip/' + ahash[0:2] + '/' + ahash[2:6] + '/' + ahash
		text_dir = static_dir + '/' + lang_id + '/text/' + thash[0:2] + '/' + thash[2:6] + '/' + thash
		#print(audio_dir)
		#print(text_dir)
		pathlib.Path(text_dir).mkdir(parents=True, exist_ok=True)
		pathlib.Path(audio_dir).mkdir(parents=True, exist_ok=True)
		audio_path = audio_dir + '/audio.mp3'
		# Symlink the audio file in the clips directory to the audio_path
		os.symlink(clips_dir + '/' + fname, audio_path)
		text_fd = open(text_dir + '/text', 'w')
		print(text, file=text_fd)
		# Symlink the text metadata file to the audio directory
		os.symlink(os.path.abspath(text_dir + '/text'), audio_dir + '/text')
		metadata = {
			'text': text,
			'tokens': [[i, j, k] for (i, j, k) in zip(tokens, labels, chars)]
		}
		metadata_fd = open(text_dir + '/info', 'w')
		json.dump(metadata, metadata_fd)
		text_fd.close()
		metadata_fd.close()
		line = cache_fd.readline()
		i+= 1

	json.dump(index, index_fd)
	index_fd.close()

	return i


if __name__ == "__main__":
	n_lines = deploy(os.path.abspath(sys.argv[1]), sys.argv[2], 'static/')

	print(n_lines,'deployed.', file=sys.stderr)

