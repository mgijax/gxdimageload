#!/bin/csh -f

#
# TR 7819
#
# Wrapper script for loading TR 7819 Image data
#
# Processing:
#	1. Load Images into PIXMGD_DB and assign PIX IDs (manual done using pixload.csh)
#	2. Load Images
#	3. Load Assay/Image associations
#

cd `dirname $0` && source ./tr7819.config

setenv LOG `basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# generate the MGI-format image files
./tr7819.py | tee -a $LOG

# process the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGI_DBUSER} -P${MGI_DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

cd ${DATADIR}

# process copyright
${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGI_DBUSER} -P${MGI_DBPASSWORDFILE} -I${COPYRIGHTFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${COPYRIGHTNOTETYPE}\" | tee -a ${LOG}

# process caption
${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGI_DBUSER} -P${MGI_DBPASSWORDFILE} -I${CAPTIONFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${CAPTIONNOTETYPE}\" | tee -a ${LOG}

# process the associations between assays and images
#./tr7819assoc.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGI_DBUSER} -P${MGI_DBPASSWORDFILE} -M${LOADMODE} | tee -a $LOG

date | tee -a $LOG

