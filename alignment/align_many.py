import argparse
import os
from collections import OrderedDict
parser = argparse.ArgumentParser(description="script {}".format(__file__))
parser.add_argument('--wav_file_dir', type=str, required=True,
                    help='string denoting the path for a folder of wav files\n')
parser.add_argument('--metadata_csv', type=str, required=True,
                    help='string denoting the path for a metadata.csv file\n')
parser.add_argument('--port', type=int, required=True,
                    help='int for the port which docker is running, ex for 0.0.0.0:49154->8765/tcp you would use 49154\n')
args = parser.parse_args()

csv_path = args.metadata_csv
wav_file_dir = args.wav_file_dir
port = args.port
with open(csv_path) as f:
     info = OrderedDict()
     for line in f:
         path, text1, text2 = line.strip().split('|')
         info[path] = text1

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

    exact_wav = wav_file_dir + "/" + wav_path + ".wav"
    run_str = 'curl -F "audio=@{}" -F "transcript=@prealignment_txts/{}.txt" "http://localhost:{}/transcriptions?async=false" > alignment_json/{}.json'.format(exact_wav, wav_path, port, wav_path)
    print("Running command {} of {}".format(n, len(info)))
    print(run_str)
    os.system(run_str)

# curl -F "audio=@eric.mp3" -F "transcript=@eric.txt" "http://localhost:8765/transcriptions?async=false" > transcribed.json
