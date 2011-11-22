#!/bin/csh -f

#
# TR 8002
#
# Wrapper script for loading TR 8002 Image data
#
# Processing:
#	1. Load Images into PixelDB and assign PIX IDs (use pixload.csh)
#	2. Load Images
#	3. Load Assay/Image associations
#

source ./tr8002.config

setenv LOG	`basename $0`.log
rm -rf $LOG
touch $LOG
 
date | tee -a $LOG
 
# load images into pixeldb
${GXDIMAGELOAD}/pixload.sh tr8002.config | tee -a ${LOG}

# generate the MGI-format image files
${GXDIMAGELOAD}/tr8002.py | tee -a $LOG

# process and load the MGI-format image files
${GXDIMAGELOAD}/gxdimageload.py | tee -a $LOG

date | tee -a $LOG

