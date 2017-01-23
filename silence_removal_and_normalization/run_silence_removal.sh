file=$1
wavname=$1

if [[ ${file: -4} == ".mp3" ]]; then
    bname=$(basename $file .mp3);
    mp3fname=$file
    wavname="$bname".wav;
    ffmpeg -i $file -af volumedetect -f null -y nul &> original.txt
    grep "max_volume" original.txt > original1.tmp
    sed -i 's|: -|=|' original1.tmp
    sed -i 's| |\r\n|' original.tmp
    sed -i 's| |\r\n|' original.tmp
    sed -i 's| |\r\n|' original.tmp
    sed -i 's| |\r\n|' original.tmp
    grep "max_volume" original1.tmp > original2.tmp
    sed -i 's|max_volume=||' original2.tmp
    yourscriptvar=$(cat "./original2.tmp" | cut -d "]" -f 2 | cut -d " " -f 2)dB
    rm result.mp3
    ffmpeg -y -i $file -af "volume=$yourscriptvar" result.mp3
    ffmpeg -y -i result.mp3 -acodec pcm_s16le -ac 1 -ar 16000 $wavname;
    noise_tolerance=50
    ffmpeg -y -i $wavname -af silenceremove=1:0:-"$noise_tolerance"dB "$bname"_out.wav 
    mv "$bname"_out.wav $wavname
fi

bname=$(basename $wavname .wav)
# lium diarization not working
#/usr/bin/java -Xmx3072m -jar ./lium_spkdiarization-8.4.1.jar --fInputMask=./"$bname".wav --sOutputMask=./"$bname".seg "$bname"
#mkdir -p seg
#mv *.seg seg
#rm "$bname".mp3

mkdir -p wav
mv *.wav wav
rm *.tmp
rm *.txt
rm *.mp3
