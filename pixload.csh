#!/bin/csh -f

#
# Program: pixload.csh
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Take a directory of jpeg files and "load" them into PixelDB.
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
echo ${JPGDIRECTORY}
echo ${OUTPUTFILE}

set accID=`cat ${PIXELDBCOUNTER}`
rm -rf ${OUTPUTFILE}
touch ${OUTPUTFILE}
echo "starting pix id: " $accID

foreach j (${JPGDIRECTORY}/*.jpg)
	set n=`basename $j`
	cp $j ${PIXELDBDATA}/$accID.jpg
	echo "$n	$accID" >> ${OUTPUTFILE}
	set accID=`expr $accID + 1`
end

rm -rf ${PIXELDBCOUNTER}
echo $accID > ${PIXELDBCOUNTER}
echo "ending pix id: " $accID

