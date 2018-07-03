from __future__ import print_function
import os
import json
import argparse

#python align_many.py /Tmp/kastner/lj_speech/LJSpeech-1.0/wavs/ /Tmp/kastner/lj_speech/LJSpeech-1.0/txts/ /Tmp/kastner/lj_speech/LJSpeech-1.0/gentle_json
parser = argparse.ArgumentParser()
parser.add_argument('jsondir', nargs=1, default=None)
parser.add_argument('outtxtdir', nargs=1, default=None)
args = parser.parse_args()

jsonfile_list = sorted([args.jsondir[0] + os.sep + jsf for jsf in os.listdir(args.jsondir[0])])
if not os.path.exists(args.outtxtdir[0]):
    os.mkdir(args.outtxtdir[0])

dd = {}
for n, jsf in enumerate(jsonfile_list):
    err_count = 1000000000000
    with open(jsf, 'r') as f:
        tj = json.load(f)
    err_count = sum([w["case"] == "not-found-in-audio" for w in tj["words"]])
    if err_count != 0:
        continue
    res = []
    oov = False
    for w in tj["words"]:
        res.append([])
        for ph in w["phones"]:
            p = ph["phone"].split("_")[0]
            if p == "oov":
                oov = True
            else:
                dd[p] = None
            res[-1].append(p)
    if oov:
        continue
    phone_str = str(" ".join(["@" + "@".join(ri) for ri in res]))
    transcript = "# " + tj["transcript"].encode("ascii", "ignore")
    base = jsf.split(os.sep)[-1][:-4] # remove .txt, and preceding path
    opf = args.outtxtdir[0] + os.sep + base + "phones"
    with open(opf, "w") as f:
        f.writelines([phone_str + "\n", transcript])
    print("Wrote output {}".format(opf))
