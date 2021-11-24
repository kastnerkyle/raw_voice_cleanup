from __future__ import print_function
import os
import subprocess
import json
import argparse

def pwrap(args, shell=False):
    p = subprocess.Popen(args, shell=shell, stdout=subprocess.PIPE,
                         stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                         universal_newlines=True)
    return p

# Print output
# http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
def execute(cmd, shell=False):
    popen = pwrap(cmd, shell=shell)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line

    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


def pe(cmd, shell=True, verbose=True):
    """
    Print and execute command on system
    """
    all_lines = []
    for line in execute(cmd, shell=shell):
        if verbose:
            print(line, end="")
        all_lines.append(line.strip())
    return all_lines

#python align_many.py /Tmp/kastner/lj_speech/LJSpeech-1.0/wavs/ /Tmp/kastner/lj_speech/LJSpeech-1.0/txts/ /Tmp/kastner/lj_speech/LJSpeech-1.0/gentle_json
parser = argparse.ArgumentParser()
parser.add_argument('wavdir', nargs=1, default=None)
parser.add_argument('txtdir', nargs=1, default=None)
parser.add_argument('outjsondir', nargs=1, default=None)
args = parser.parse_args()

wavfile_list = sorted([args.wavdir[0] + os.sep + wvf for wvf in os.listdir(args.wavdir[0])])
txtfile_list = sorted([args.txtdir[0] + os.sep + txf for txf in os.listdir(args.txtdir[0])])
if not os.path.exists(args.outjsondir[0]):
    os.mkdir(args.outjsondir[0])

# try to match every txt file and every wav file by name
wv_bases = sorted([str(os.sep).join(wv.split(os.sep)[:-1]) for wv in wavfile_list])
tx_bases = sorted([str(os.sep).join(tx.split(os.sep)[:-1]) for tx in txtfile_list])
wv_names = sorted([wv.split(os.sep)[-1] for wv in wavfile_list])
tx_names = sorted([tx.split(os.sep)[-1] for tx in txtfile_list])
wv_i = 0
tx_i = 0
wv_match = []
tx_match = []
while True:
    if tx_i >= len(tx_names) or wv_i >= len(wv_names):
        break
    if "." in tx_names[tx_i]:
        tx_part = ".".join(tx_names[tx_i].split(".")[:1])
    else:
        # support txt files with no ext
        tx_part = tx_names[tx_i]
    wv_part = ".".join(wv_names[wv_i].split(".")[:1])
    if wv_part == tx_part:
        wv_match.append(wv_bases[wv_i] + os.sep + wv_names[wv_i])
        tx_match.append(tx_bases[tx_i] + os.sep + tx_names[tx_i])
        wv_i += 1
        tx_i += 1
    else:
        print("WAV AND TXT NAMES DIDN'T MATCH AT STEP, ADD LOGIC")
        from IPython import embed; embed(); raise ValueError()

assert len(wv_match) == len(tx_match)
for n, (wvf, txf) in enumerate(zip(wv_match, tx_match)):
    base = txf.split(os.sep)[-1][:-4] # remove .txt, and preceding path
    ojf = args.outjsondir[0] + os.sep + base + ".json"
    err_count = 1000000000000
    if os.path.exists(ojf):
        with open(ojf, 'r') as f:
            tj = json.load(f)
        err_count = sum([w["case"] == "not-found-in-audio" for w in tj["words"]])
        for w in tj["words"]:
            if "phones" in w:
                phones = [wp["phone"] for wp in w["phones"]]
        # don't reprocess if it is already perfect...
        # this also allows to rerun and catch edge cases where it (can) return a failure
        if err_count == 0:
            continue
    print("Aligning {}/{}, {}:{}".format(n + 1, len(wv_match), wvf, txf))
    cmd = "python gentle/align.py --disfluency {} {}".format(wvf, txf)
    try:
        res = pe(cmd, verbose=False)
        rj = json.loads("".join(res))
        err_count_new = sum([w["case"] == "not-found-in-audio" for w in rj["words"]])
        if err_count_new < err_count:
            print("Writing out {}".format(ojf))
            with open(ojf, 'w') as f:
                 json.dump(rj, f, sort_keys=False, indent=4,
                           ensure_ascii=True)
    except:
        print("Unknown exception, continuing...")
