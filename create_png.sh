#!/bin/bash
text=$@
text=`sed "s/ /   /g" <<<$text`
convert -background black \
-gravity Center \
-size 760x380 \
-fill white \
-pointsize 50 \
caption:"$text" \
-extent 960x480 \
./img/current.png