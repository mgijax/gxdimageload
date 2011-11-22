#!/bin/csh -f

#
# TR 8985
#
# Wrapper script for loading TR 8985 Image data
#

source ./tr8985.config

setenv LOG	`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# create file of image files
${GXDIMAGELOAD}/tr8985.py

# process and load the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py | tee -a $LOG

date | tee -a $LOG

