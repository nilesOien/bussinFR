#!/bin/bash


rm -f up.png
rm -f stopped_bus.png
rm -f stop.png

magick back-arrow-3095.png -rotate 90.0 up.png

rm -rf output
mkdir output

angle=0
while [ "$angle" -le 350 ]
do

 angle=$(echo "$angle" | awk '{printf("%03d", $1)}')

 echo $angle

 magick up.png -distort SRT "$angle" output/arrow_"$angle".png
 magick output/arrow_"$angle".png -resize 20x20 output/arrow_"$angle".png
 magick output/arrow_"$angle".png -transparent white output/arrow_"$angle".png

 angle=`expr "$angle" + 10`
done

cp up.png stopped_bus.png
magick stopped_bus.png -fill white -draw "rectangle 30,90 100,40" stopped_bus.png
magick stopped_bus.png -transparent white stopped_bus.png
magick stopped_bus.png -resize 20x20 stopped_bus.png

magick -size 20x20 xc:red stop.png
magick stop.png -fill green -draw "rectangle 3,3 17,17" stop.png
magick stop.png -fill blue -draw "rectangle 6,6 14,14" stop.png
magick stop.png -fill red -draw "rectangle 9,9 11,11" stop.png

cp -v stop.png ../webpages/icons/stop.png 
cp -v stopped_bus.png ../webpages/icons/
cp -v output/*.png ../webpages/arrows/


exit 0

