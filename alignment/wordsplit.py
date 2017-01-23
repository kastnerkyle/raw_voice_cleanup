# Author: Kyle Kastner
# License: BSD 3-Clause
# Based on example from
# http://stackoverflow.com/questions/2174093/detect-most-likely-words-from-text-without-spaces-combined-words
# Get wordlist from
# https://github.com/hermitdave/FrequencyWords/raw/master/content/2016/en/en_full.txt
"""
# Example WORD_FREQUENCIES
WORD_FREQUENCIES = {
    'file': 0.00123,
    'files': 0.00124,
    'save': 0.002,
    'ave': 0.00001,
    'as': 0.00555
}
"""
import os
import sys

WORD_FREQUENCIES = {}
sum_num = 0
with open("en_full.txt", "r") as f:
    l = f.readlines()

s = sum([int(li.strip().split(" ")[1]) for li in l])
for li in l:
    k, v = li.strip().split(" ")
    v = float(v) / s
    WORD_FREQUENCIES[k] = v

def split_text(text, word_frequencies, cache):
    if text in cache:
        return cache[text]
    if not text:
        return 1, []
    best_freq, best_split = 0, []
    for i in range(1, len(text) + 1):
        word, remainder = text[:i], text[i:]
        freq = word_frequencies.get(word, None)
        if freq:
            remainder_freq, remainder = split_text(
                    remainder, word_frequencies, cache)
            freq *= remainder_freq
            if freq > best_freq:
                best_freq = freq
                best_split = [word] + remainder
    cache[text] = (best_freq, best_split)
    return cache[text]

infile = "wordlist.txt"
with open(infile, "r") as f:
    text = f.readlines()

splitfile = "words2split.txt"
if not os.path.exists(splitfile):
    with open(splitfile, "w") as f:
        lucache = {}
        for ti in text:
            tt = ti.strip().lower()
            res = split_text(tt, WORD_FREQUENCIES, lucache)
            if len(res[1]) > 1:
                f.write(tt + ":" + " ".join(res[1]) + "\n")

replace_lu = {}
with open(splitfile, "r") as f:
    l = f.readlines()
    l = [li.strip().lower() for li in l]
    for li in l:
        k, v = li.split(":")
        replace_lu[k] = v

if len(sys.argv) < 2:
    raise ValueError("Need argument for file to fix")

replacefile = sys.argv[1]
with open(replacefile, "r") as f:
    l = f.readlines()
ws = l[0].split(" ")
res = []
for w in ws:
    wl = w.lower()
    if wl in replace_lu.keys():
        res.extend(replace_lu[wl].split(" "))
    else:
        res.append(wl)

with open(replacefile, "w") as f:
    f.write(" ".join(res) + "\n")
