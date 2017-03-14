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

# http://stackoverflow.com/questions/8982163/how-do-i-tell-python-to-convert-integers-into-words
"""Given an int32 number, print it in English."""
def int_to_en(num):
    d = { 0 : 'zero', 1 : 'one', 2 : 'two', 3 : 'three', 4 : 'four', 5 : 'five',
          6 : 'six', 7 : 'seven', 8 : 'eight', 9 : 'nine', 10 : 'ten',
          11 : 'eleven', 12 : 'twelve', 13 : 'thirteen', 14 : 'fourteen',
          15 : 'fifteen', 16 : 'sixteen', 17 : 'seventeen', 18 : 'eighteen',
          19 : 'nineteen', 20 : 'twenty',
          30 : 'thirty', 40 : 'forty', 50 : 'fifty', 60 : 'sixty',
          70 : 'seventy', 80 : 'eighty', 90 : 'ninety' }
    k = 1000
    m = k * 1000
    b = m * 1000
    t = b * 1000

    assert(0 <= num)

    if (num < 20):
        return d[num]

    if (num < 100):
        if (num % 10) == 0: return d[num]
        else: return d[num // 10 * 10] + '-' + d[num % 10]

    if (num < k):
        if (num % 100) == 0: return d[num // 100] + ' hundred'
        else: return d[num // 100] + ' hundred and ' + int_to_en(num % 100)

    if (num < m):
        if (num % k) == 0: return int_to_en(num // k) + ' thousand'
        else: return int_to_en(num // k) + ' thousand, ' + int_to_en(num % k)

    if (num < b):
        if (num % m) == 0: return int_to_en(num // m) + ' million'
        else: return int_to_en(num // m) + ' million, ' + int_to_en(num % m)

    if (num < t):
        if (num % b) == 0: return int_to_en(num // b) + ' billion'
        else: return int_to_en(num // b) + ' billion, ' + int_to_en(num % b)

    if (num % t) == 0: return int_to_en(num // t) + ' trillion'
    else: return int_to_en(num // t) + ' trillion, ' + int_to_en(num % t)

    raise AssertionError('num is too large: %s' % str(num))


def has_digit(s):
    return any(i.isdigit() for i in s)


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
    elif has_digit(wl):
        # assume digits are contiguous, and only one set
        digit_inds = [n for n, _ in enumerate(wl) if _.isdigit()]
        digit_start = digit_inds[0]
        digit_end = digit_inds[-1] + 1
        try:
	    digit = wl[digit_start:digit_end]
	    word_digit = int_to_en(int(digit)) 
            pre = wl[:digit_start]
            post = wl[digit_end:]
            if len(pre) > 0:
                res.append(pre)
            res.append(word_digit)
            if len(post) > 0:
                res.append(post)
        except KeyError:
            res.append(wl)
        except TypeError:
            import pdb; pdb.set_trace()
    else:
        res.append(wl)

with open(replacefile, "w") as f:
    f.write(" ".join(res) + "\n")
