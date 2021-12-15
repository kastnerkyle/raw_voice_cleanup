from phoneme_tools.eng_rules import hybrid_g2p
import argparse
import os
import json
import shutil

parser = argparse.ArgumentParser(description="script {}".format(__file__))
parser.add_argument('--check_json', type=str, default="failure_alignment_json",
                    help='folder of json to check\n')
parser.add_argument('--check_txts', type=str, default="failure_prealignment_txts",
                    help='folder of txts to check\n')

args = parser.parse_args()
prealignment_folder = args.check_txts
alignment_folder = args.check_json

def grapheme_pronounciation(sent):
    # adds _S to signify singleton, assume the phoneme set is the same as or a subset of, full_phones.txt
    r = hybrid_g2p(sent)
    els = [ri.split("@") for ri in r.split(" ")]
    all_els = []
    for eli in els:
        all_els.append([ee + "_S" for ee in eli if ee != ""])
    return all_els

names = [os.path.splitext(f)[0] for f in sorted(os.listdir(alignment_folder))]
alignment_json_paths = [alignment_folder + os.path.sep + n + ".json" for n in names]
prealignment_txt_paths = [prealignment_folder + os.path.sep + n + ".txt" for n in names]

pronunciation_out_txts_folder = "pronunciation_prealignment_txts"
if not os.path.exists(pronunciation_out_txts_folder):
    os.mkdir(pronunciation_out_txts_folder)

pronunciation_out_json_folder = "pronunciation_alignment_json"
if not os.path.exists(pronunciation_out_json_folder):
    os.mkdir(pronunciation_out_json_folder)

checks = ["noise", "sil", "oov", "#", "laughter", "<eps>"]
for prealignment_txt, alignment_json in list(zip(prealignment_txt_paths, alignment_json_paths)):
    with open(alignment_json, "r") as f:
        alignment = json.load(f)

    new_alignment_words = []
    for n, el in enumerate(alignment["words"]):
        # set a flag if there's a failed alignment, won't have phones!
        if "phones" in el:
            p = el["phones"]
            failed_checks = False
            for c in checks:
                for pi in p:
                    if c in pi["phone"]:
                        failed_checks = True
        else:
            failed_checks = True

        if failed_checks or el["case"] != "success":
            g2p_pred = grapheme_pronounciation(el["word"])[0]
            # fake end offset start offset durations
            new_el = {}
            new_el["case"] = "success"
            new_el["alignedWord"] = el["word"]
            new_el["startOffset"] = el["startOffset"]
            new_el["endOffset"] = el["endOffset"]
            if n > 0:
                new_el["start"] = last_el["end"] + 0.005
            else:
                new_el["start"] = 0.0

            if n != (len(alignment["words"]) - 1):
                if "start" in alignment["words"][n + 1]:
                    new_el["end"] = alignment["words"][n + 1]["start"] - 0.005
                else:
                    # make proxy ending based on scaling of the offset ratio
                    ratio = last_el["end"] / float(last_el["endOffset"])
                    new_el["end"] = last_el["endOffset"] * ratio
            else:
                # make proxy ending based on scaling of the offset ratio
                ratio = last_el["end"] / float(last_el["endOffset"])
                new_el["end"] = last_el["endOffset"] * ratio
            # just assume equal duration on the phones
            est_end = new_el["end"]
            est_start = new_el["start"]
            if est_end <= est_start:
                est_end = est_start
            est_dur = (est_end - est_start) / len(g2p_pred)
            new_phones = [{"duration": est_dur, "phone": g2p_pred_p} for g2p_pred_p in g2p_pred]
            new_el["phones"] = new_phones
            new_alignment_words.append(new_el)
        else:
            new_el = el
            new_alignment_words.append(el)
        last_el = new_el
    out_alignment = {}
    out_alignment["transcript"] = alignment["transcript"]
    out_alignment["words"] = new_alignment_words

    with open(pronunciation_out_json_folder + os.sep + os.path.basename(alignment_json), "w") as f:
        json.dump(out_alignment, f)

    shutil.copy2(prealignment_txt, pronunciation_out_txts_folder + os.sep + os.path.basename(prealignment_txt))
