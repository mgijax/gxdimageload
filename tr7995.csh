#!/bin/csh -f

#
# TR 7995
#
# Wrapper script for loading TR 7995 Image data
#
# Processing:
#	1. Load Images into PIXMGD_DB and assign PIX IDs (manuall done using pixload.csh)
#	2. Load Images
#	3. Load Assay/Image associations
#

cd `dirname $0` && source ./tr7995.config

setenv LOG `basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# generate the MGI-format image files
./tr7995.py | tee -a $LOG

# process the MGI-format image files
${GXDIMAGELOAD} -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

# process copyright
${MGINOTELOAD} -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${COPYRIGHTFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${COPYRIGHTNOTETYPE}\" | tee -a ${LOG}

# process caption
${MGINOTELOAD} -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${CAPTIONFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${CAPTIONNOTETYPE}\" | tee -a ${LOG}

# process the associations between assays and images
./tr7995assoc.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

date | tee -a $LOG

