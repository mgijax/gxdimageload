#!/bin/csh -f

#
# TR 6118
#
# Wrapper script for loading TR 6118 image data
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
pixload.csh ${GXDIMGLOADDATADIR}/tr6118/images ${GXDIMGLOADDATADIR}/pix91257.txt >>& $LOG

# generate the MGI-format image files
J91257.py >>& $LOG
# process the MGI-format image files
gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG
# process the associations between assays and images
J91257assoc.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG

date >> $LOG

