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
 
#pixload.csh ${GXDIMGLOADDATADIR}/tr4800/images/10.5dpc ${GXDIMGLOADDATADIR}/pix10.5.txt >>& $LOG
#pixload.csh ${GXDIMGLOADDATADIR}/tr4800/images/14.5dpc ${GXDIMGLOADDATADIR}/pix14.5.txt >>& $LOG

#J80502-10.5.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} >>& $LOG
#gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG

J80502-14.5.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} >>& $LOG
gxdimageload.py -S${DBSERVER} -D${DBNAME} -U${DBUSER} -P${DBPASSWORDFILE} -M${LOADMODE} >>& $LOG

date >> $LOG

