mkdir -p txt
for i in wav/*; do
    bname=$(basename $i .wav)
    cp raw_txt/"$bname".txt tmp.txt
    cat tmp.txt | tr "\n" "-" | tr -d "-" | tr -s " " | tr "\." "\. " | tr -s " " > tmp2.txt
    cat tmp2.txt | tr -d "\(" | tr -d "\)" | sed -e 's/Applause//g' | sed -e 's/&nbs;p;//g' | tr -s " " | tr -s "." > tmp3.txt
    cat tmp3.txt | sed -e 's/\ \.\ /\./g' | sed -e 's/\ \.//g' | sed -e 's/&n;bsp;//g' | sed -e 's/&nbsp;//g' > tmp4.txt
    cat tmp4.txt | sed -e 's/\(\.\)\(.\)/\. \2/g' | sed -e 's/THEPRESIDENT//g' | tr -s " " > tmp5.txt
    cat tmp5.txt | sed -e 's/9;//g' | sed -e 's// /g' | sed -e 's/THE PRESIDENT//g' | tr -d ":" | tr -d "'" | tr -s " " > tmp6.txt
    cat tmp6.txt | sed -e 's/&nb;sp;//g' | sed -e 's/Laughter//g' | LANG=C sed 's/[\d128-\d255]//g' | sed -e 's/Q //g' | sed -e 's/Q\.//g' | sed -e 's/\<p\>//g' | tr -d "<" | tr -d ">" | tr -s " " > tmp7.txt
    cat tmp7.txt | sed -e 's/&#39;//g' | tr -s " " > tmp8.txt
    mv tmp8.txt txt/"$bname".txt
    rm tmp*txt
done

grep -o -E '\w+' txt/* | sort -u -f | cut -d ":" -f 2 | sort -u -f > wordlist.txt

for i in txt/*; do
    python wordsplit.py $i
done

gentledir=gentle
if [ ! -d "$gentledir" ]; then
    bash build_gentle.sh
fi
