#!/bin/csh -f

#
# TR 5154
#
# Wrapper script for loading TR 5154 image data
#
# Processing:
#	1. Load Images into PIXDB and assign PIX IDs
#	2. Load Images
#	3. Load Assay/Image associations
#

cd `dirname $0` && source ./Configuration

setenv LOG $0.log
rm -rf $LOG
touch $LOG
 
date > $LOG
 
# process the image files; load them into pixeldb and assign pix ids
pixload.csh ${GXDIMGLOADDATADIR}/tr5154/images/unzipped ${GXDIMGLOADDATADIR}/pix80501.txt >>& $LOG

# generate the MGI-format image files
J80501.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} >>& $LOG
# process the MGI-format image files
gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG
# process the associations between assays and images
J80501assoc.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG

date >> $LOG

