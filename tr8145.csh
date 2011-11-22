#!/bin/csh -f

#
# TR 8145
#
# Wrapper script for loading TR 8145 Image data
#

source ./tr8145.config

setenv LOG	`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# generate the MGI-format image files
${GXDIMAGELOAD}/tr8145.py | tee -a $LOG

# process and load the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py | tee -a $LOG

date | tee -a $LOG

