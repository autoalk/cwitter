#!/bin/bash

msg=$@
OIFS=$IFS
IFS="/"
c=0
fr_fac=100

for i in $msg;
do
	((c+=1))
	bash create_png.sh $i
	mv ./img/current.png ./img/part$c.png
done


IFS=$OIFS
this_args=""
for i in `seq $c`;
do 
	this_len=`cat ./len/$i.txt | tr -d " \t\n\r"`
	this_len=`echo $this_len*$fr_fac|bc -l`
	this_args="$this_args -delay $this_len ./img/part$i.png"
done
convert $this_args -loop 0 ./img/total.gif