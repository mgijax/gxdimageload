#!/bin/csh

# $Header$
# $Name$

#
# Program: pixload.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Take a directory of jpeg files and "load" them into
#	PixelDB.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	pixload.csh [JPG File Directory] [output file]
#
#	example: pixload.csh data/tr4800/images/10.5dpc pix10.5dpc
#
# Envvars:
#
# Inputs:
#
#	A directory containing jpeg files
#
# Outputs:
#
#	An tab-delimited output file of:
#		jpeg filename
#		pixel DB id
#
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#
#    Modules:
#
# Modification History:
#
#	07/15/2003 lec
#	- created
#

cd `dirname $0` && source ./Configuration

setenv JPGDIRECTORY	$1
setenv OUTPUTFILE	$2

set accID=`cat $PIXELDBCOUNTER`
rm -rf $OUTPUTFILE
touch $OUTPUTFILE
echo "starting pix id: " $accID

#foreach j ($JPGDIRECTORY/*.jpg)

foreach j ($JPGDIRECTORY/0*.jpg)
	set n=`basename $j .jpg`
	echo $n
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$n	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
end
foreach j ($JPGDIRECTORY/1*.jpg)
	set n=`basename $j .jpg`
	echo $n
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$n	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
end
foreach j ($JPGDIRECTORY/2*.jpg)
	set n=`basename $j .jpg`
	echo $n
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$n	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
end
foreach j ($JPGDIRECTORY/6*.jpg)
	set n=`basename $j .jpg`
	echo $n
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$n	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
end
foreach j ($JPGDIRECTORY/e*.jpg)
	set n=`basename $j .jpg`
	echo $n
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$n	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
end
foreach j ($JPGDIRECTORY/p*.jpg)
	set n=`basename $j .jpg`
	echo $n
	cp $j $PIXELDBDATA/$accID.jpg
	echo "$n	$accID" >> $OUTPUTFILE
	set accID=`expr $accID + 1`
end

rm -rf $PIXELDBCOUNTER
echo $accID > $PIXELDBCOUNTER
echo "ending pix id: " $accID

