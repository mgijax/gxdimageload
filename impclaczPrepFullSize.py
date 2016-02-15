#!/usr/local/bin/python

#
#  impclaczPrepFullSize.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the fullsize images.
#
#  Usage:
#
#      impclaczPrepFullSize.py
#
#  Env Vars:
#
#      PIXELDBDATA
#      PIX_MAPPING
#      IMAGE_FILE
#      IMAGEPANE_FULLSIZE
#      REFERENCE
#
#  Inputs:
#
#      PIX_MAPPING- Tab-delimited fields:
#
#          1) File name of the fullsize image that has been added to pixel DB
#          2) Accession number from pixel DB (numeric part)
#
#  Outputs:
#
#      IMAGE_FILE - Tab-delimited fields:
#
#          1) Reference (J:171409)
#          2) Fullsize image key (blank)
#          3) Image Class (_Vocab_key = 83)
#          4) Pixel DB accession number (numeric part)
#          5) X dimension of the image
#          6) Y dimension of the image
#          7) Figure label
#          8) Copyright note
#          9) Caption note
#          10) Image info
#
#      IMAGEPANE_FILE - Tab-delimited fields:
#
#           1) PIX ID (PIX:####)
#           2: Pane Label
#           3) X Dimension (width)
#           4) Y Dimension (heigth)
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#
#  Assumes:  Nothing
#
#  Notes:  None
#
###########################################################################

import sys
import os
import string
import jpeginfo

#
#  CONSTANTS
#
FULLSIZE_IMAGE_KEY = ''
URL = ''

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA'] # /data/pixeldb
pixFile = os.environ['PIX_MAPPING'] # this is pixeload mapping file
inFile = os.environ['INPUT_FILE'] # Connie's input file
imageFile = os.environ['IMAGEFILE'] #  gxdimageload IMG_Image input file
imagePaneFile = os.environ['IMAGEPANEFILE'] # gxdimageload IMG_Pane input file
jNumber = os.environ['REFERENCE']
imageLookup = {}
#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def initialize ():
    global fpPixFile, fpInFile, fpImageFile, fpImagePaneFile
    global imageLookup

    #
    # Open pixelDB mapping file.
    #
    try:
        fpPixFile = open(pixFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + pixFile + '\n')
        sys.exit(1)


    #
    # Open Connie's input file
    #
    try:
        fpInFile = open(inFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + inFile + '\n')
        sys.exit(1)

    #
    # Open the output files.
    #
    try:
        fpImageFile = open(imageFile, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imageFile + '\n')
        sys.exit(1)

    try:
        fpImagePaneFile = open(imagePaneFile, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imagePaneFile + '\n')
        sys.exit(1)

    # load pixDB mapping file
    for line in fpPixFile.readlines():
	impcName, pixID = string.split(line)
	impcName = impcName.replace('.jpg', '')
	
	imageLookup[impcName] = pixID
    return


#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def closeFiles ():
    fpPixFile.close()
    fpInFile.close()
    fpImageFile.close()
    fpImagePaneFile.close()

    return


#
# Purpose: Create the image and image pane output files for each pixel DB
#          image that is being added.
# Returns: 0 if successful, 1 for an error
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def process ():

    #
    # Process each line of the input file.
    #
    counter = 0
    header = fpInFile.readline()
    for line in fpInFile.readlines():

	counter += 1

        #
        # Tokenize the lines from the pixload mapping file and get the original image 
        # file names (e.g. JAX-JAX_001-IMPC_ALZ_001-IMPC_ALZ_075_001-433341.jpg) and 
	# the pix ID that represents the new image file name in pixel DB.
        #
        tokens = string.split(line[:-1], '\t')
	jNumber = tokens[0]
	imageType = tokens[2]
	figureLabel = tokens[6]
	copyright = tokens[7]
	caption = tokens[8]
	if not imageLookup.has_key(figureLabel):
	    continue

	pixID = '%s' % imageLookup[figureLabel]
	image = '%s/%s.jpg' % (pixelDBDir, pixID)   
	(xdim, ydim) = jpeginfo.getDimensions(image)
	fpImageFile.write(jNumber + '\t' +
			  FULLSIZE_IMAGE_KEY + '\t' +
			  imageType + '\t' +
			  pixID + '\t' +
			  str(xdim) + '\t' +
			  str(ydim) + '\t' +
			  figureLabel + '\t' +
			  copyright + '\t' +
			  caption + '\t' +
			  URL + '\n')

	fpImagePaneFile.write(pixID + '\t\t' + str(xdim) + '\t' + str(ydim) + '\n')

    print counter
    return 0


#
# Main
#
print 'initializing'
initialize()
print 'processing'
process()
print 'closing files'
closeFiles()

sys.exit(0)
