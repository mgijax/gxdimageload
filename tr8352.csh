#!/bin/csh

#
# TR 8352
#
# Wrapper script for loading TR 8352 Image data
#

source ./tr8352.config

setenv LOG	`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# process and load the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py | tee -a $LOG

date | tee -a $LOG

