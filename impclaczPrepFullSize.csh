#!/bin/csh -f

#
# IMPC LacZ Image load
#

cd `dirname $0` && source ./impclacz.config

setenv LOGNAME	`basename $0`.log
setenv LOG	"${DATADIR}/${LOGNAME}"
setenv NOTEDATADIR	${DATADIR}

echo $LOG
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# process and load the MGI-format image files
${GXDIMAGELOAD}/impclaczPrepFullSize.py >& ${LOG}
${GXDIMAGELOAD}/gxdimageload.py  >>& ${LOG}

# mginoteload.py puts output in the current directory
cd ${DATADIR}

# process copyright
 ${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${COPYRIGHTFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${COPYRIGHTNOTETYPE}\" | tee -a ${LOG}
#
# # process caption
 ${NOTELOAD}/mginoteload.py -S${MGD_DBSERVER} -D${MGD_DBNAME} -U${MGD_DBUSER} -P${MGD_DBPASSWORDFILE} -I${CAPTIONFILE} -M${NOTELOADMODE} -O${OBJECTTYPE} -T\"${CAPTIONNOTETYPE}\" | tee -a ${LOG}
#
date | tee -a $LOG

