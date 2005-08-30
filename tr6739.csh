#!/bin/csh -f

#
# TR 6739
#
# Wrapper script for loading TR 6739 image data
#
# Processing:
#	1. Load Assay/Image associations
#

cd `dirname $0` && source ./Configuration

setenv LOG ${LOGDIR}/`basename $0`.log
rm -rf $LOG
 
date > $LOG
 
#
#  Create the associations between assay results and image files.
#
echo "" >>& $LOG
echo "Call tr6739assoc.py" >>& $LOG
${GXDIMGLOADINSTALLDIR}/tr6739assoc.py >>& $LOG

date >> $LOG

