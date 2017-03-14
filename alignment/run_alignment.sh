# Need to make this consistent
txtdir=txt
if [ ! -d "$txtdir" ]; then
    mkdir -p txt
    for i in wav/*; do
        bname=$(basename $i .wav)
        cp raw_txt/"$bname".txt tmp.txt
        cat tmp.txt | tr ";" " " | tr "\n" "-" | tr -d "-" | tr -s " " | tr "\." "\. " | tr -s " " > tmp2.txt
        cat tmp2.txt | tr -d "\(" | tr -d "\)" | sed -e 's/Applause//g' | sed -e 's/&nbsp//g' | tr -s " " | tr -s "." > tmp3.txt
        cat tmp3.txt | sed -e 's/\ \.\ /\./g' | sed -e 's/\ \.//g' > tmp4.txt
        cat tmp4.txt | sed -e 's/\(\.\)\(.\)/\. \2/g' | sed -e 's/THEPRESIDENT//g' | tr -s " " > tmp5.txt
        cat tmp5.txt | sed -e 's/9//g' | sed -e 's// /g' | sed -e 's/THE PRESIDENT//g' | tr -d ":" | tr -d "'" | tr -s " " > tmp6.txt
        cat tmp6.txt | sed -e 's/Laughter//g' | LANG=C sed 's/[\d128-\d255]//g' | sed -e 's/Q //g' | sed -e 's/Q\.//g' | sed -e 's/\<p\>//g' | tr -d "<" | tr -d ">" | tr -s " " > tmp7.txt
        cat tmp7.txt | sed -e 's/&#39//g' | sed -e 's/&mdash/ /g' | sed -e 's/$//g' | sed -e 's/,/ , /g' | sed -e 's/,//g' > tmp8.txt
        cat tmp8.txt | sed -e 's/\./\. /g' | sed -e 's|/||g' | sed -e 's/\$//g' | sed -e 's/&nbs/ /g' | sed -e 's/ \. /\. /g' | tr -s " " > tmp9.txt
        cat tmp9.txt | sed -e 's/,//g' | sed -e 's/ \./\./g' | sed -e 's/&n bsp/ /g' | sed -e 's/"//g' | sed -e 's/-//g' | sed -e 's/\[//g' | sed -e 's/\]//g' | tr -s " " > tmp10.txt
        cat tmp10.txt | sed -e 's/&m dash/ /g' | sed -e 's/\?/\./g' | tr -s "." | tr -s " " > tmp11.txt
        mv tmp11.txt txt/"$bname".txt
        rm tmp*txt
    done

    grep -o -E '\w+' txt/* | sort -u -f | cut -d ":" -f 2 | sort -u -f > wordlist.txt

    for i in txt/*; do
        python wordsplit.py $i
    done
fi

gentledir=gentle
if [ ! -d "$gentledir" ]; then
    bash build_gentle.sh
fi

segdir=seg
if [ ! -d "$segdir" ]; then
    mkdir -p seg
    for i in txt/*; do
        bname=$(basename $i .txt)
        wavmatch=wav/"$bname".wav
        jsonmatch=seg/"$bname".json
        python gentle/align.py $wavmatch $i > res.json
        mv res.json $jsonmatch 
    done
fi

python wavseg.py spe_1960_0715_kennedy.json
