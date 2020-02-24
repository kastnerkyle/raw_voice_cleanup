import sys
import io
import os

if len(sys.argv) < 3:
    print("Pass path to metadata.csv as first argument, directory for output of txt files in the second argument!")
    sys.exit()

metadata = sys.argv[1]
txt_path = sys.argv[2]

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
            continue
        full = os.path.join(txt_path, basename + ".txt")
        with open(full, "w") as of:
            of.writelines([content])
