import sys
import io
import os

if len(sys.argv) < 3:
    print("Pass path to metadata.csv as first argument, directory for output of txt files in the second argument!")
    sys.exit()

metadata = sys.argv[1]
txt_path = sys.argv[2]

skipped_wav = []
with io.open(metadata, encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('|')
        basename = parts[0]
        content = parts[2]
        if content[-1] not in [";", ",", ".", "?", "!"]:
            content = content + "~"
        try:
            content = content.decode("ascii")
        except UnicodeEncodeError:
            print("Non-ascii input found in {}, skipping - consider deleting the corresponding wav file".format(basename))
            skipped_wav.append(basename + ".wav")
            continue
        full = os.path.join(txt_path, basename + ".txt")
        with open(full, "w") as of:
            of.writelines([content])

delname = "wav_to_delete_meta.txt"
with open(delname, "w") as o:
    o.writelines([s + "\n" for s in skipped_wav])

print("Wrote out proposed deletion filenames to {}".format(delname))
print("You can use this file by `cd` into the firectory of wav files, and using xargs like:")
print("xargs -a /home/kkastner/src/raw_voice_cleanup/alignment/wav_to_delete_meta.txt -d'\\n' rm")
