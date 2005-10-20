#!/bin/csh

cd `dirname $0` && source ./tr7167.config

setenv JPGDIRECTORY	KuoImages
setenv OUTPUTFILE	${DATADIR}/KuoImages.txt

set accID=`cat $PIXELDBCOUNTER`
rm -rf $OUTPUTFILE
touch $OUTPUTFILE
echo "starting pix id: " $accID

cd $JPGDIRECTORY
foreach i (`ls -d *`)
	echo $i
	cd $i
	foreach j (*.jpg)
	ls -l $j
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$i	$j	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
	end
	cd ..
end

rm -rf $PIXELDBCOUNTER
echo $accID > $PIXELDBCOUNTER
echo "ending pix id: " $accID

