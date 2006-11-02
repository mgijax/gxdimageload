#!/bin/sh

#
# Program: pixload.sh
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
#	pixload.sh ConfigFile
#
#	example: pixload.sh tr8002.config
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

. $1

accID=`cat ${PIXELDBCOUNTER}`
rm -rf ${PIXFILE}
touch ${PIXFILE}
echo "starting pix id: " $accID

for j in ${IMAGESDIR}/*.jpg
do
	n=`basename $j`
	echo $n
	cp $j ${PIXELDBDATA}/$accID.jpg
	echo "$n	$accID" >> ${PIXFILE}
	accID=`expr $accID + 1`
done

rm -rf ${PIXELDBCOUNTER}
echo $accID > ${PIXELDBCOUNTER}
echo "ending pix id: " $accID

