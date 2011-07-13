#!/bin/sh
#
#  tr10629pixload.sh
###########################################################################
#
#  Purpose:  This script will copy all of the image files (fullsize
#            and thumbnails) to the pixel DB directory and rename them
#            using the next available accession number.  It also creates
#            output files that are used during preprocessing for the
#            GXD image load.
#
#  Usage:
#
#      tr10629pixload.sh
#
#  Env Vars:
#
#      PIXELDB_FILES
#      PIX_FULLSIZE
#      PIX_THUMBNAIL
#      PIX_MISSING
#
#  Inputs:
#
#      - Pixel DB accession counter (/data/pixeldb/accession/counter).  This
#        file contains the first accession number to be used.
#
#      - PixelDBFileList.txt (PIXELDB_FILES) which contains a list of all of
#        the image file.
#
#  Outputs:
#
#      - Pix_Fullsize.txt (PIX_FULLSIZE) which contains a list of all of
#        the fullsize image files that are being added to pixel DB.  The
#        file has the following tab-delimited fields:
#
#            1) Image file name (e.g. euxassay_000001_01.jpg)
#            2) Accession number (e.g. 82345)
#
#      - Pix_Thumbnail.txt (PIX_THUMBNAIL) which contains a list of all of
#        the thumbnail image files that are being added to pixel DB.  The
#        file has the following tab-delimited fields:
#
#            1) Image file name (e.g. euxassay_000001_01.jpg)
#            2) Accession number (e.g. 82345)
#
#      - Pix_MissingFiles.txt (PIX_MISSING) which contains a list of all of
#        the image files (fullsize and thumbnail) that are missing.
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

cd `dirname $0`

if [ ! -f ${PIXELDB_FILES} ]
then
    echo "Missing file: ${PIXELDB_FILES}"
    exit 1
fi

#
# Get the first accession number to be used.
#
ACCID=`cat ${PIXELDBCOUNTER}`

rm -f ${PIX_FULLSIZE} ${PIX_THUMBNAIL} ${PIX_MISSING}
touch ${PIX_FULLSIZE} ${PIX_THUMBNAIL} ${PIX_MISSING}

echo "Starting pix id: ${ACCID}"
for FILENAME in `cut -f3 ${PIXELDB_FILES} | cat`
do
    #
    # If the image file is in the fullsize directory, copy it to the
    # pixel DB directory, renaming it with the next accession number.
    # Write the original file name and accession number to the fullsize
    # image list.  If the image file does not exist, write the file
    # name to the missing file list.
    #
    if [ -f ${FULLSIZE_IMAGE_DIR}/${FILENAME} ]
    then
        PIXELDBFILE=${PIXELDBDATA}/${ACCID}.jpg
        cp ${FULLSIZE_IMAGE_DIR}/${FILENAME} ${PIXELDBFILE}
        echo "${FILENAME}	${ACCID}" >> ${PIX_FULLSIZE}
        LAST_ACCID=${ACCID}
        ACCID=`expr ${ACCID} + 1`
    else
        echo "${FULLSIZE_IMAGE_DIR}/${FILENAME}" >> ${PIX_MISSING}
    fi

    #
    # If the image file is in the thumbnail directory, copy it to the
    # pixel DB directory, renaming it with the next accession number.
    # Write the original file name and accession number to the thumbnail
    # image list.  If the image file does not exist, write the file
    # name to the missing file list.
    #
    if [ -f ${THUMBNAIL_IMAGE_DIR}/${FILENAME} ]
    then
        PIXELDBFILE=${PIXELDBDATA}/${ACCID}.jpg
        cp ${THUMBNAIL_IMAGE_DIR}/${FILENAME} ${PIXELDBFILE}
        echo "${FILENAME}	${ACCID}" >> ${PIX_THUMBNAIL}
        LAST_ACCID=${ACCID}
        ACCID=`expr ${ACCID} + 1`
    else
        echo "${THUMBNAIL_IMAGE_DIR}/${FILENAME}" >> ${PIX_MISSING}
    fi
done
echo "Ending pix id: ${LAST_ACCID}"

#
# Advance the pixel DB counter to the next available accession number.
#
echo "Advance pixel DB counter to: ${ACCID}"
${ACCID} > ${PIXELDBCOUNTER}
