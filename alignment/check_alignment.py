import os
import json
import shutil
from text_cleaning import clean_text
import argparse
import sys

parser = argparse.ArgumentParser(description="script {}".format(__file__))
parser.add_argument('--no_expand_abbreviation', default=False, action="store_true",
                    help='dont do abbreviation expansion (applicable for TTS generated data)\n')
parser.add_argument('--copy_out_failures', default=False, action="store_true",
                    help='copy out to proposed folder\n')
parser.add_argument('--no_write', default=False, action="store_true",
                    help='dont write anything out\n')
parser.add_argument('--dump_failures', default=False, action="store_true",
                    help='dump list of failure file basenames to "failures.txt"\n')
parser.add_argument('--check_json', type=str, default="alignment_json",
                    help='folder of json to check\n')
parser.add_argument('--check_txts', type=str, default="prealignment_txts",
                    help='folder of txts to check\n')

args = parser.parse_args()
prealignment_folder = args.check_txts
alignment_folder = args.check_json
copy_out_failures = args.copy_out_failures
no_write = args.no_write
no_expand_abbreviation = args.no_expand_abbreviation
dump_failures = args.dump_failures

names = [os.path.splitext(f)[0] for f in sorted(os.listdir(alignment_folder))]
alignment_json_paths = [alignment_folder + os.path.sep + n + ".json" for n in names]
prealignment_txt_paths = [prealignment_folder + os.path.sep + n + ".txt" for n in names]

not_found_prealignment = []
not_found_alignment = []
for prealignment_txt, alignment_json in list(zip(prealignment_txt_paths, alignment_json_paths)):
    if not os.path.exists(prealignment_txt):
        not_found_prealignment.append(prealignment_txt)
    if not os.path.exists(alignment_json):
        not_found_alignment.append(alignment_json)

if len(not_found_prealignment) > 0:
    raise ValueError("Did not find the following prealignment files {}".format(not_found_prealignment))
if len(not_found_alignment) > 0:
    raise ValueError("Did not find the following alignment files {}".format(not_found_alignment))


failed_to_align = []
elements_of_failure = []
for prealignment_txt, alignment_json in list(zip(prealignment_txt_paths, alignment_json_paths)):
    with open(alignment_json, "r") as f:
        try:
            alignment = json.load(f)
        except:
            failed_to_align.append((prealignment_txt, alignment_json))
            elements_of_failure.append(("", None))
            continue

    for el in alignment["words"]:
        if el["case"] != "success":
            if len(failed_to_align) > 0:
                # if a sentence has multiple failures dont add multiple times
                if failed_to_align[-1][0] != prealignment_txt:
                    failed_to_align.append((prealignment_txt, alignment_json))
            elif len(failed_to_align) == 0:
                failed_to_align.append((prealignment_txt, alignment_json))
            elements_of_failure.append((alignment["transcript"], el))

failed_to_check = []
phones_of_failure = []
checks = ["noise", "sil", "oov", "#", "laughter", "<eps>"]
for prealignment_txt, alignment_json in list(zip(prealignment_txt_paths, alignment_json_paths)):
    with open(alignment_json, "r") as f:
        try:
            alignment = json.load(f)
        except:
            failed_to_check.append((prealignment_txt, alignment_json))
            phones_of_failure.append(("", None))
            continue

    # set a flag if there's a failed alignment, won't have phones!
    skip_to_next = False
    for el in alignment["words"]:
        if el["case"] != "success":
            skip_to_next = True

    if skip_to_next:
        continue

    phones = [el["phones"] for el in alignment["words"]]
    for el in alignment["words"]:
        p = el["phones"]
        failed_checks = False
        for c in checks:
            for pi in p:
                if c in pi["phone"]:
                    failed_checks = True
        if failed_checks:
            if len(failed_to_check) > 0:
                # if a sentence has multiple failures dont add multiple times
                if failed_to_check[-1][0] != prealignment_txt:
                    failed_to_check.append((prealignment_txt, alignment_json))
            elif len(failed_to_check) == 0:
                failed_to_check.append((prealignment_txt, alignment_json))
            phones_of_failure.append((alignment["words"], el))

out_folder = "proposed_prealignment_txts"
assert out_folder != prealignment_folder
assert out_folder != alignment_folder

if dump_failures:
    failure_lines = []
    if len(failed_to_check) > 0 or len(failed_to_align) > 0:
        print("Some examples failed due to detection of unmatched text or invalid phone symbols in {}".format(checks))
        print("{} files failed alignment check".format(len(failed_to_align)))
        print("{} files failed phone check".format(len(failed_to_check)))
        print("Dumping failures to failures.txt")
        for prealignment_txt, alignment_json in failed_to_check + failed_to_align:
            base1 = os.path.basename(prealignment_txt)
            final_base1 = os.path.splitext(base1)[0]
            base2 = os.path.basename(alignment_json)
            final_base2 = os.path.splitext(base2)[0]
            assert final_base1 == final_base2
            failure_lines.append(final_base1)

    with open("failures.txt", "w") as f:
         f.writelines([l + "\n" for l in failure_lines])

if not os.path.exists(out_folder):
    os.mkdir(out_folder)

if copy_out_failures or no_write:
    print("{} files failed alignment check".format(len(failed_to_align)))
    print("{} files failed phone check".format(len(failed_to_check)))
    if no_write:
        sys.exit()

if copy_out_failures:
    print("Copying failed txts to failure_prealignment_txts")
    print("Copying failed json to failure_alignment_json")
    out_txts_folder = "failure_prealignment_txts"
    out_json_folder = "failure_alignment_json"
    if not os.path.exists(out_txts_folder):
        os.mkdir(out_txts_folder)
    if not os.path.exists(out_json_folder):
        os.mkdir(out_json_folder)
    for prealignment_txt, alignment_json in failed_to_check + failed_to_align:
        shutil.copy2(prealignment_txt, out_txts_folder + os.sep + os.path.basename(prealignment_txt))
        shutil.copy2(alignment_json, out_json_folder + os.sep + os.path.basename(alignment_json))

if copy_out_failures or dump_failures or no_write:
    sys.exit()

if len(failed_to_check) > 0 or len(failed_to_align) > 0:
    print("Some examples failed due to detection of unmatched text or invalid phone symbols in {}".format(checks))
    print("{} files failed alignment check".format(len(failed_to_align)))
    print("{} files failed phone check".format(len(failed_to_check)))
    print("Creating corrections and writing to proposed_prealignment_txts, you can rerun align_many.py with the txts_dir argument to re-process")
    for prealignment_txt, alignment_json in failed_to_check + failed_to_align:
        base = os.path.basename(prealignment_txt)
        with open(prealignment_txt, "r") as f:
             lines = f.readlines()
        line = lines[0]
        try:
            if no_expand_abbreviation:
                clean_line = clean_text(line, ["english_no_expand_abbreviation_cleaners"])
            else:
                clean_line = clean_text(line, ["english_cleaners"])
        except:
            print("Exception in cleaners")
            from IPython import embed; embed(); raise ValueError()
        with open(out_folder + os.sep + base, "w") as f:
            f.write(clean_line + "\n")
