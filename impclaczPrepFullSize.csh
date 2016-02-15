#!/bin/csh -f

#
# IMPC LacZ Image load
#

source ./impclacz.config

setenv LOGNAME	`basename $0`.log
setenv LOG	"${DATADIR}/${LOGNAME}"
echo $LOG
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# process and load the MGI-format image files
${GXDIMAGELOAD}/impclaczPrepFullSize.py >& ${LOG}
${GXDIMAGELOAD}/gxdimageload.py  >>& ${LOG}

date | tee -a $LOG

