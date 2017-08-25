#!/bin/bash
source config.sh

msg=$@
tlen=0
wlen=0
c=0
soxargs=""
for i in `seq ${#msg}`;
do
	this_char=${msg:$i-1:1}
	if [ "$this_char" = " " -o "$this_char" = "." -o "$this_char" = "-" -o "$this_char" = "/" ];then
		if [ "$this_char" != "/" ];then
			#echo $i: $this_char
			if  [ "$this_char" = "." ];then
				this_len=$dit_len
				this_freq=$freq
			elif [ "$this_char" = "-" ];then
				this_len=$dah_len
				this_freq=$freq
			elif [ "$this_char" = " " ];then
				this_len=$spc_len
				this_freq=0
			fi
			sox -n ./audio/part$i.wav  synth $this_len sin $this_freq pad $end_len fade l 0:$fade 0 0:$fade;
			wlen=`echo $wlen+$this_len+$end_len|bc -l`
			tlen=`echo $tlen+$this_len+$end_len|bc -l`
			soxargs="$soxargs ./audio/part$i.wav "
		elif [ "$this_char" = "/" ];then
			((c+=1))
			echo $wlen > ./len/$c.txt			
			wlen=0
		
		fi
		
		
	
	fi
done
((c+=1))
echo $wlen > ./len/$c.txt


sox $soxargs ./audio/total.wav

echo $tlen
rm ./audio/part*