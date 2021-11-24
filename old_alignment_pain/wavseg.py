import json
import sys
import numpy as np
from scipy.io import wavfile
import os

json_path = sys.argv[1]

# This should be chunk sizes in seconds
split_chunk = 12
split_size = 8
drop_chunk = 4

# minimum words to count as an utterance
min_words = 5

wav_in_path = "wav"
txt_in_path = "txt"
wav_out_path = "seg_wav"
txt_out_path = "seg_txt"

with open(json_path, 'r') as f:
    d = json.load(f)

full_transcript = d["transcript"]
all_words = d["words"]
"""
w = all_words[0]
w.keys()
[u'case',
 u'end',
 u'endOffset',
 u'phones',
 u'alignedWord',
 u'start',
 u'startOffset',
 u'word']
"""
valid_stop_bounds = []
valid_start_bounds = []
stopped = True
last_valid = -1
for n, wi in enumerate(all_words):
    if not stopped and wi['case'] == 'not-found-in-audio':
        valid_stop_bounds.append(all_words[last_valid]['end'])
        stopped = True
    elif stopped and wi['case'] == 'success':
        stopped = False
        valid_start_bounds.append(wi['start'])
    if wi['case'] == 'success':
        last_valid = n

if len(valid_start_bounds) != len(valid_stop_bounds):
    assert abs(len(valid_start_bounds) - len(valid_stop_bounds)) == 1
    if len(valid_start_bounds) > len(valid_stop_bounds):
        valid_start_bounds = valid_start_bounds[:len(valid_stop_bounds)]

bounds = list(zip(valid_start_bounds, valid_stop_bounds))
base_time_diff = [stop - start for start, stop in bounds]

# remove under X second chunks
to_keep = [n for n, _ in enumerate(base_time_diff) if _ > drop_chunk]
bounds = [b for n, b in enumerate(bounds) if n in to_keep]
time_diff = [stop - start for start, stop in bounds]

def dynamic_match(bounds, words):
    # gnarly attempt at dynamic programming
    # to match bounds and words, accounting for "not-found-in-audio" chunks
    kept = []
    for nb, b in enumerate(bounds):
        for nw, w in enumerate(words):
            if w['case'] == 'not-found-in-audio':
                # try our best to make contiguous chunks
                last_val_w = None
                for y in list(range(nw))[::-1]:
                    if all_words[y]['case'] != 'not-found-in-audio':
                        last_val_w = words[y]
                        break

                next_val_w = None
                for z in list(range(nw + 1, len(all_words))):
                    if all_words[z]['case'] != 'not-found-in-audio':
                        next_val_w = all_words[z]
                        break

                if last_val_w is None:
                    continue

                if last_val_w['start'] > b[1]:
                    break
                elif next_val_w is None or next_val_w['end'] < b[0]:
                    continue
                elif next_val_w['start'] < b[1]:
                    if last_val_w['end'] > b[0]:
                        # only use it if nearby context
                        if abs(y - nw) < 3:
                            if abs(z - nw) < 3:
                                kept.append((nb, w))
            else:
                if w['start'] > b[1]:
                    break
                elif w['end'] < b[0]:
                    continue
                elif w['start'] < b[1]:
                    if w['end'] < b[1]:
                        kept.append((nb, w))
    return kept


def split_on_max_gap(words):
    # split in half on maximum gap
    starts = []
    ends = []
    for nw, w in enumerate(words):
        if w['case'] != 'not-found-in-audio':
            starts.append(w['start'])
            ends.append(w['end'])
        else:
            last_val_w = None
            for y in list(range(nw))[::-1]:
                if words[y]['case'] != 'not-found-in-audio':
                    last_val_w = words[y]
                    break

            next_val_w = None
            for z in list(range(nw + 1, len(words))):
                if words[z]['case'] != 'not-found-in-audio':
                    next_val_w = all_words[z]
                    break

            if last_val_w is None:
                if next_val_w is None:
                    raise ValueError("didn't find any forward or previous valid data")
                last_val_w = w
                if 'start' in next_val_w.keys():
                    last_val_w['end'] = next_val_w['start']
            elif next_val_w is None:
                if last_val_w is None:
                    raise ValueError("didn't find any forward or previous valid data")
                next_val_w = w
                if 'end' in last_val_w.keys():
                    next_val_w['start'] = last_val_w['end']
            if 'end' in last_val_w.keys() and 'start' in next_val_w.keys():
                starts.append(last_val_w['end'])
                ends.append(next_val_w['start'])
    # global def for split_chunk
    if ends[-1] - starts[0] < split_chunk:
        return words
    gaps = [s - e for s, e in zip(starts[1:], ends[:-1])]
    gap_inds = [n + 1 for n in range(len(gaps))]
    max_ind = np.argmax(gaps)
    slice_point = gap_inds[max_ind]
    return (words[:slice_point], words[slice_point:])


def recursive_split(words, split_limit):
    if len(words) > split_limit:
        r = split_on_max_gap(words)
        rout = []
        for ri in r:
            out = recursive_split(ri, split_limit)
            rout.append(out)
        return rout
    else:
        return words

kept = dynamic_match(bounds, all_words)

# split > X sec chunks into approximate sentence level...
to_split = [n for n, _ in enumerate(time_diff) if _ > split_chunk]
# bound indexes and values
all_bounds = [(n, b) for n, b in enumerate(bounds)]
split_bounds = [(n, b) for n, b in enumerate(bounds) if n in to_split]

def flatten(S):
    if S == []:
        return S
    if isinstance(S[0], list):
        return flatten(S[0]) + flatten(S[1:])
    return S[:1] + flatten(S[1:])


def recurse_bounds(tree):
    try:
        len(tree[0][0])
    except KeyError:
        # in a leaf
        try:
            s = None
            for i in range(len(tree)):
                if "start" in tree[i].keys():
                    s = tree[i]['start']
                    break
            e = None
            for ii in range(len(tree))[::-1]:
                if "end" in tree[ii].keys():
                    e = tree[ii]['end']
                    break
            if s is None or e is None:
                raise KeyError()
        except KeyError:
            raise ValueError("Key error in bounds recursion")
            #from IPython import embed; embed()
            #raise ValueError()
        return [(s, e)]
    res_i = []
    for i in range(len(tree)):
        res_i.extend(recurse_bounds(tree[i]))
    # flatten it out
    return flatten(res_i)

# find new bounds for split_bounds
split_bound_indices = [i[0] for i in split_bounds]
final_bounds = []
for nb, b in enumerate(bounds):
    if nb not in split_bound_indices:
        if len(b) == 2:
            final_bounds.append(b)
        continue
    w_in_b = [k[1] for k in kept if k[0] == nb]
    r = recursive_split(w_in_b, split_size)
    rb = recurse_bounds(r)
    final_bounds.extend(rb)

final_words = dynamic_match(final_bounds, all_words)

wav_base = json_path.split("/")[-1].split(".")[0]
wav_name = wav_base + ".wav"

if not os.path.exists(wav_out_path):
    os.mkdir(wav_out_path)

if not os.path.exists(txt_out_path):
    os.mkdir(txt_out_path)

wav_read_path = wav_in_path + "/" + wav_name
fs, wav_d = wavfile.read(wav_read_path)

def bounds_to_sample_indices(s, e):
    # bounds in seconds
    # returns indices
    s_i = int(s * fs)
    s_e = int(e * fs) + 1
    return s_i, s_e

ids = range(len(final_bounds))
ids = sorted(list(set(ids)))
for ii in ids:
    w = [w_i for id_i, w_i in final_words if id_i == ii]
    s_w = None
    f_s_i = None
    for s_i in range(len(w)):
        if 'start' in w[s_i].keys():
            s_w = w[s_i]['start']
            f_s_i = s_i
            break

    e_w = None
    f_e_i = None
    for e_i in range(len(w))[::-1]:
        if 'end' in w[e_i].keys():
            e_w = w[e_i]['end']
            f_e_i = e_i
            break

    if s_w is None or e_w is None:
        continue

    if s_w >= e_w:
        continue

    w_clear = w[f_s_i:f_e_i + 1]
    w_sent = []
    for w_c in w_clear:
        if 'alignedWord' in w_c.keys():
            w_sent.append(w_c['alignedWord'])
        else:
            #print("no alignedWord")
            w_sent.append(w_c['word'])

    sub_txt = " ".join(w_sent)
    if len(w_sent) < min_words:
        continue

    si, se = bounds_to_sample_indices(s_w, e_w)
    sub_wav = wav_d[si:se]
    sub_wav_out_path = wav_base + "_{0:04d}.wav".format(ii)
    sub_wav_out_path = wav_out_path + "/" + sub_wav_out_path
    wavfile.write(sub_wav_out_path, fs, sub_wav)

    sub_txt_out_path = wav_base + "_{0:04d}.txt".format(ii)
    sub_txt_out_path = txt_out_path + "/" + sub_txt_out_path
    with open(sub_txt_out_path, "w") as f:
        f.writelines([sub_txt])
