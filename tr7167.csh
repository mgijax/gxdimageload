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

setenv LOG $0.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
cd ${DATADIR}

# process the image files; load them into pixeldb and assign pix ids
tr7167pixload.csh | tee -a $LOG

# generate the MGI-format image files
tr7167.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} | tee -a $LOG

# process the MGI-format image files
${GXDIMAGELOAD} -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

# process copyright
${MGINOTELOAD} -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -I${COPYRIGHTFILE} -M${LOADMODE} -O${OBJECTTYPE} -T\"${NOTETYPE}\" | tee -a ${LOG}

# process the associations between assays and images
tr7167assoc.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

date | tee -a $LOG

