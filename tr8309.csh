#!/bin/csh -f

#
# TR 8309
#
# Wrapper script for loading TR 8309 Image data
#

source ./tr8309.config

setenv LOG	`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# process and load the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py | tee -a $LOG

date | tee -a $LOG

