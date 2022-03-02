import argparse
import os
from collections import OrderedDict
import sys
parser = argparse.ArgumentParser(description="script {}".format(__file__))
parser.add_argument('--wav_file_dir', type=str, required=True,
                    help='string denoting the path for a folder of wav files\n')
parser.add_argument('--metadata_csv', type=str, default=None,
                    help='string denoting the path for a metadata.csv file\n')
parser.add_argument('--prealignment_only', default=False, action="store_true",
                    help='copy out prealignment texts from metadata and exit\n')
parser.add_argument('--txts_dir', type=str, default=None,
                    help='string denoting path for prealignment txts, overrides metadata csv\n')
parser.add_argument('--port', type=int, required=True,
                    help='int for the port which docker is running, ex for 0.0.0.0:49154->8765/tcp you would use 49154\n')
args = parser.parse_args()

csv_path = args.metadata_csv
wav_file_dir = args.wav_file_dir
port = args.port
txts_dir = args.txts_dir
prealignment_only = args.prealignment_only

if csv_path is not None:
    with open(csv_path) as f:
         info = OrderedDict()
         for line in f:
             path, text1, text2 = line.strip().split('|')
             info[path] = text2

    missing = OrderedDict()
    for wav_path in sorted(info.keys()):
        if not os.path.exists(wav_file_dir + "/" + wav_path + ".wav"):
            missing[wav_path] = True

    if len(missing) > 0:
        raise ValueError("Mismatch between metadata files and wav, correct this manually by deleting related lines from metadata.csv file!\nOffending lines {}".format(missing))

    if not os.path.exists("prealignment_txts"):
        os.mkdir("prealignment_txts")

    if not os.path.exists("alignment_json"):
        os.mkdir("alignment_json")

    for n, wav_path in enumerate(sorted(info.keys())):
        with open("prealignment_txts/" + wav_path + ".txt", "w") as f:
            f.write(info[wav_path])

    if prealignment_only:
        sys.exit()

    # handle clean restarting
    base_keys = sorted(info.keys())

    possible_corrupted_wav = []
    for b_k in base_keys:
        # check if the actual wav file seems corrupted
        exact_wav = wav_file_dir + os.sep + b_k + ".wav"
        # see 166 bytes for failures many times
        if os.path.getsize(exact_wav) < 1000:
            possible_corrupted_wav.append(b_k)

    if len(possible_corrupted_wav) > 0:
        for el in possible_corrupted_wav:
            print(el)
        print("Found several possible corrupted wav files (wav filesize < 1k bytes)")
        print("Remove these entries from metadata.csv and the core dataset wav dir and try again")
        print("Example to remove these lines from metadata csv")
        print("#python align_many.py --wav_file_dir=/usr/local/data/kkastner/lessac_blizzard/wavs/ --metadata_csv=/usr/local/data/kkastner/lessac_blizzard/metadata.csv --port=8765 | grep -v grep | grep segments > exclude.txt; grep -v -f exclude.txt /usr/local/data/kkastner/lessac_blizzard/metadata.csv > filtered_metadata.csv")
        print("Example to list these files programmatically:")
        print("#for i in $(python align_many.py --wav_file_dir=/usr/local/data/kkastner/lessac_blizzard/wavs/ --metadata_csv=/usr/local/data/kkastner/lessac_blizzard/metadata.csv --port=8765 | grep -v grep | grep segments); do ls -lh /usr/local/data/kkastner/lessac_blizzard/wavs/$i.wav; done")
        sys.exit()

    did_first_print = False
    keys_to_run = []
    for b_k in base_keys:
        json_path = "alignment_json" + os.sep + b_k + ".json"
        if os.path.exists(json_path):
            if not did_first_print:
                print("found existing files, trying to continue from last correct file output")
                did_first_print = True
            if os.path.getsize(json_path) == 0:
                keys_to_run.append(b_k)
                # delete the 0 byte file
                os.remove(json_path)
        else:
            keys_to_run.append(b_k)


    for n, wav_path in enumerate(keys_to_run):
        exact_wav = wav_file_dir + "/" + wav_path + ".wav"
        run_str = 'curl -F "audio=@{}" -F "transcript=@prealignment_txts/{}.txt" "http://localhost:{}/transcriptions?async=false" > alignment_json/{}.json'.format(exact_wav, wav_path, port, wav_path)
        print("Running command {} of {}".format(n, len(keys_to_run)))
        print(run_str)
        os.system(run_str)
    # curl -F "audio=@eric.mp3" -F "transcript=@eric.txt" "http://localhost:8765/transcriptions?async=false" > transcribed.json
else:
    # this path runs if you pass txts_dir
    assert txts_dir is not None
    base_names = os.listdir(txts_dir)
    info = OrderedDict()
    for bn in base_names:
        with open(txts_dir + os.sep + bn, "r") as f:
            lines = f.readlines()
        line = lines[0].strip()
        path = bn.split(".")[0]
        info[path] = line

    out_json_folder = "proposed_alignment_json"
    if not os.path.exists(out_json_folder):
        os.mkdir(out_json_folder)

    # handle clean restarting
    base_keys = sorted(info.keys())

    possible_corrupted_wav = []
    for b_k in base_keys:
        # check if the actual wav file seems corrupted
        exact_wav = wav_file_dir + os.sep + b_k + ".wav"
        if os.path.exists(exact_wav):
            # see 166 bytes for failures many times
            if os.path.getsize(exact_wav) < 1000:
                possible_corrupted_wav.append(b_k)
        else:
            possible_corrupted_wav.append(b_k)

    if len(possible_corrupted_wav) > 0:
        for el in possible_corrupted_wav:
            print(el)
        print("Found several possible corrupted wav files (wav filesize < 1k bytes)")
        print("Remove these entries from prealignment_txts and the core dataset wav dir and try again")
        print("Example to list these files programmatically:")
        print("#for i in $(python align_many.py --txts_dir=proposed_prealignment_txts/ --wav_file_dir=/usr/local/data/kkastner/lessac_blizzard/wavs --port=8765 | grep -v grep | grep segments); do ls -lh proposed_prealignment_txts/$i.txt; ls -lh /usr/local/data/kkastner/lessac_blizzard/wavs/$i.wav; done")
        sys.exit()

    did_first_print = False
    keys_to_run = []
    for b_k in base_keys:
        json_path = out_json_folder + os.sep + b_k + ".json"
        if os.path.exists(json_path):
            if not did_first_print:
                print("found existing files, trying to continue from last correct file output")
                did_first_print = True
            if os.path.getsize(json_path) == 0:
                keys_to_run.append(b_k)
                # delete the 0 byte file
                os.remove(json_path)
        else:
            keys_to_run.append(b_k)

    for n, wav_path in enumerate(keys_to_run):
        exact_wav = wav_file_dir + "/" + wav_path + ".wav"
        run_str = 'curl -F "audio=@{}" -F "transcript=@{}" "http://localhost:{}/transcriptions?async=false" > {}/{}.json'.format(exact_wav, txts_dir + os.sep + wav_path + ".txt", port, out_json_folder, wav_path)
        print("Running command {} of {}".format(n, len(keys_to_run)))
        print(run_str)
        os.system(run_str)
