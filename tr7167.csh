#!/bin/csh -f

#
# TR 7167
#
# Wrapper script for loading TR 7167 Image data
#
# Processing:
#	1. Load Images into PIXDB and assign PIX IDs
#	2. Load Images
#	3. Load Assay/Image associations
#

cd `dirname $0` && source ./tr7167.config

cd ${DATADIR}

setenv LOG `basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# process the image files; load them into pixeldb and assign pix ids
${GXDIMAGELOAD}/tr7167pixload.csh | tee -a $LOG

# generate the MGI-format image files
${GXDIMAGELOAD}/tr7167.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} | tee -a $LOG

# process the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

# process copyright
${NOTELOAD}/mginoteload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${COPYRIGHTFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${COPYRIGHTNOTETYPE}\" | tee -a ${LOG}

# process caption
${NOTELOAD}/mginoteload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${CAPTIONFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${CAPTIONNOTETYPE}\" | tee -a ${LOG}

# process the associations between assays and images
${GXDIMAGELOAD}/tr7167assoc.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

date | tee -a $LOG

