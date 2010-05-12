#!/bin/sh
#
#  pixload.sh
###########################################################################
#
#  Purpose:  This script will copy all of the best image files (fullsize
#            and thumbnails) to the pixel DB directory and rename them
#            using the next available accession number.  It also creates
#            output files that are used during preprocessing for the
#            GXD image load.
#
#  Usage:
#
#      pixload.sh
#
#  Env Vars:
#
#      PIXELDB_FILES
#      PIX_FULLSIZE
#      PIX_THUMBNAIL
#
#  Inputs:
#
#      - Pixel DB accession counter (/data/pixeldb/accession/counter).  This
#        file contains the first accession number to be used.
#
#      - FULLSIZE_IMAGE_DIR
#
#      - THUMBNAIL_IMAGE_DIR
#
#  Outputs:
#
#      - Pix_Fullsize.txt (PIX_FULLSIZE) which contains a list of all of
#        the fullsize image files that are being added to pixel DB.  The
#        file has the following tab-delimited fields:
#
#            1) Image file name (e.g. 1700009P17Rik_E7.5_lat.jpg)
#            2) Accession number (e.g. 45678)
#
#      - Pix_Thumbnail.txt (PIX_THUMBNAIL) which contains a list of all of
#        the thumbnail image files that are being added to pixel DB.  The
#        file has the following tab-delimited fields:
#
#            1) Image file name (e.g. 1700009P17Rik_E7.5_lat.jpg)
#            2) Accession number (e.g. 45678)
#
#      - Pixel DB accession counter (/data/pixeldb/accession/counter).  This
#        file is updated with the next available number.
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  Fatal error occurred
#
#  Assumes:  Nothing
#
#  Implementation:
#
#  Notes:  None
#
###########################################################################

# Get the first accession number to be used.
#
ACCID=`cat ${PIXELDBCOUNTER}`

echo ${PIX_FULLSIZE}
rm -f ${PIX_FULLSIZE}
touch ${PIX_FULLSIZE}
#rm -f ${PIX_THUMBNAIL}
#touch ${PIX_THUMBNAIL}

echo "Starting pix id: ${ACCID}"
cd ${FULLSIZE_IMAGE_DIR}
for FILE in `ls ${FULLSIZE_IMAGE_DIR}`
do
    PIXELDBFILE=${PIXELDBDATA}/${ACCID}.jpg
#    cp ${FILE} ${PIXELDBFILE}
    echo "${FILE}	${ACCID}" >> ${PIX_FULLSIZE}
    LAST_ACCID=${ACCID}
    ACCID=`expr ${ACCID} + 1`
done

echo "Starting pix id: ${ACCID}"
cd ${THUMBNAIL_IMAGE_DIR}
for FILE in `ls ${THUMBNAIL_IMAGE_DIR}`
do
    PIXELDBFILE=${PIXELDBDATA}/${ACCID}.jpg
#    cp ${FILE} ${PIXELDBFILE}
    echo "${FILE}	${ACCID}" >> ${PIX_THUMBNAIL}
    LAST_ACCID=${ACCID}
    ACCID=`expr ${ACCID} + 1`
done
echo "Ending pix id: ${LAST_ACCID}"

# Advance the pixel DB counter to the next available accession number.
#
echo "Advance pixel DB counter to: ${ACCID}"
#echo ${ACCID} > ${PIXELDBCOUNTER}

