#!/bin/csh -f

#
# TR 4800
#
# Wrapper script for loading TR 4800 image data
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
#pixload.csh ${GXDIMGLOADDATADIR}/tr4800/images/10.5dpc ${GXDIMGLOADDATADIR}/pix10.5.txt >>& $LOG
#pixload.csh ${GXDIMGLOADDATADIR}/tr4800/images/14.5dpc ${GXDIMGLOADDATADIR}/pix14.5.txt >>& $LOG

# generate the MGI-format image files
J80502-10.5.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} >>& $LOG
# process the MGI-format image files
gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG
# process the associations between assays and images
J80502-10.5assoc.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG

# generate the MGI-format image files
J80502-14.5.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} >>& $LOG
# process the MGI-format image files
gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG
# process the associations between assays and images
J80502-14.5assoc.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG

date >> $LOG

