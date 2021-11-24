import argparse
import os
parser = argparse.ArgumentParser(description="script {}".format(__file__))
parser.add_argument('--wav_file_dir', type=str, required=True,
                    help='string denoting the path for a folder of wav files\n')
parser.add_argument('--metadata_csv', type=str, required=True,
                    help='string denoting the path for a metadata.csv file\n')
args = parser.parse_args()

csv_path = args.metadata_csv
wav_file_dir = args.wav_file_dir
with open(csv_path) as f:
     info = {}
     for line in f:
         path, text1, text2 = line.strip().split('|')
         info[path] = text1

for wav_path in sorted(info.keys()):
    assert os.path.exists(wav_file_dir + "/" + wav_path + ".wav")

if not os.path.exists("prealignment_txts"):
    os.mkdir("prealignment_txts")

if not os.path.exists("alignment_json"):
    os.mkdir("alignment_json")

for n, wav_path in enumerate(sorted(info.keys())):
    with open("prealignment_txts/" + wav_path + ".txt", "w") as f:
        f.write(info[wav_path])

    exact_wav = wav_file_dir + "/" + wav_path + ".wav"
    run_str = 'curl -F "audio=@{}" -F "transcript=@prealignment_txts/{}.txt" "http://localhost:8765/transcriptions?async=false" > alignment_json/{}.json'.format(exact_wav, wav_path, wav_path)
    print("Running command {} of {}".format(n, len(info)))
    print(run_str)
    os.system(run_str)

# curl -F "audio=@eric.mp3" -F "transcript=@eric.txt" "http://localhost:8765/transcriptions?async=false" > transcribed.json
