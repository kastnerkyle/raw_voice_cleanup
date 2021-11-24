from __future__ import print_function
import os
import json
import argparse
from scipy.io import wavfile
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import math

#python json2phones.py /Tmp/kastner/lj_speech/LJSpeech-1.0/wavs/ /Tmp/kastner/lj_speech/LJSpeech-1.0/gentle_json outdir
parser = argparse.ArgumentParser()
parser.add_argument('wavdir', nargs=1, default=None)
parser.add_argument('jsondir', nargs=1, default=None)
parser.add_argument('outtxtdir', nargs=1, default=None)
args = parser.parse_args()

jsonfile_list = sorted([args.jsondir[0] + os.sep + jsf for jsf in os.listdir(args.jsondir[0])])
if not os.path.exists(args.outtxtdir[0]):
    os.mkdir(args.outtxtdir[0])

wavfile_match = {wavf[:-4]: args.wavdir[0] + os.sep + wavf for wavf in os.listdir(args.wavdir[0])}

timing_agg = []
dd = {}
for n, jsf in enumerate(jsonfile_list):
    err_count = 1000000000000
    with open(jsf, 'r') as f:
        tj = json.load(f)
    err_count = sum([w["case"] == "not-found-in-audio" for w in tj["words"]])
    if err_count != 0:
        continue
    res = []
    sils = []
    oov = False
    prev_start = 0
    prev_end = 0
    for w in tj["words"]:
        this_end = w["end"]
        this_start = w["start"]
        res.append([])
        sil = this_start - prev_end
        sils.append(sil)
        for ph in w["phones"]:
            p = ph["phone"].split("_")[0]
            if p == "oov":
                oov = True
            else:
                dd[p] = None
            res[-1].append(p)
        prev_start = this_start
        prev_end = this_end
    if oov:
        continue
    lu = jsf[:-5].split(os.sep)[-1]
    wavf = wavfile_match[lu]
    info = wavfile.read(wavf)
    dur = len(info[1]) / float(info[0])
    sil_e = abs(round(dur - prev_end, 4))
    sils.append(sil_e)
    siils = [abs(round(s, 4)) for s in sils]
    timing_agg += [si for si in sils]
    phone_str = str(" ".join(["@" + "@".join(ri) for ri in res]))
    transcript = "# " + tj["transcript"].encode("ascii", "ignore")
    gaps = "## " + " ".join([str(s) for s in sils])
    base = jsf.split(os.sep)[-1][:-4] # remove .txt, and preceding path
    opf = args.outtxtdir[0] + os.sep + base + "phones"
    with open(opf, "w") as f:
        f.writelines([phone_str + "\n", transcript + "\n", gaps])
    print("Wrote output {}".format(opf))

plt.hist(timing_agg, 100)
plt.savefig("tmphist")

data_sorted = np.sort(timing_agg)
data_sorted = data_sorted[data_sorted > 0.001]
nbins = 4
step = int(math.ceil(len(data_sorted)//nbins+1))
binned_data = []
for i in range(0,len(data_sorted),step):
    binned_data.append(data_sorted[i:i+step])
print([np.median(bd) for bd in binned_data])
from IPython import embed; embed(); raise ValueError()
