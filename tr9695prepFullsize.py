#!/usr/local/bin/python

#
#  tr9695prepFullsize.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the fullsize images.
#
#  Usage:
#
#      tr9695prepFullsize.py
#
#  Env Vars:
#
#      PIXELDBDATA
#      PIX_FULLSIZE
#      IMAGE_FULLSIZE
#      IMAGEPANE_FULLSIZE
#      REFERENCE
#
#  Inputs:
#
#      Pix_Fullsize.txt - Tab-delimited fields:
#
#          1) File name of the fullsize image that has been added to pixel DB
#          2) Accession number from pixel DB (numeric part)
#
#  Outputs:
#
#      image_Fullsize.txt - Tab-delimited fields:
#
#          1) Reference (J:153498)
#          2) Fullsize image key (blank)
#          3) Pixel DB accession number (numeric part)
#          4) X dimension of the image
#          5) Y dimension of the image
#          6) Figure label
#          7) Copyright note
#          8) Caption note
#
#      imagepane_Fullsize.txt - Tab-delimited fields:
#
#          1) Pixel DB accession number (numeric part)
#          2) Panel label (blank)
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
import re
import jpeginfo

#
#  CONSTANTS
#
CAPTION = '''This image was contributed directly to GXD by the Eurexpress database.  'Virtual' microscope zoom capability for this image and additional images can be accessed via the Eurexpress link at the bottom of this page.'''
COPYRIGHT = '''Questions regarding this image or its use in publications should be directed to the Eurexpress project support@eurexpress.org.'''

FULLSIZE_IMAGE_KEY = ''

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_FULLSIZE']
imageFile = os.environ['IMAGE_FULLSIZE']
imagePaneFile = os.environ['IMAGEPANE_FULLSIZE']
jNumber = os.environ['REFERENCE']


#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpPixFile, fpImageFile, fpImagePaneFile

    #
    # Open the input file.
    #
    try:
        fpPixFile = open(pixFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + pixFile + '\n')
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
    line = fpPixFile.readline()
    while line:

        #
        # Tokenize the input record and get the original image files name
        # (e.g. euxassay_000001_01.jpg) and the pix ID that represents the
        # new image file name in pixel DB.
        #
        tokens = re.split('\t', line[:-1])
        filename =  tokens[0]
        pixID = tokens[1]

        #
        # The figure label is derived from the image file name by removing
        # the ".jpg" suffix.
        #
        figureLabel = filename[0:-4]

        #
        # Get the X an Y dimensions of the image file in pixel DB.
        #
        (xdim, ydim) = jpeginfo.getDimensions(pixelDBDir + '/' + pixID + '.jpg')

        fpImageFile.write(jNumber + '\t' +
                          FULLSIZE_IMAGE_KEY + '\t' +
                          pixID + '\t' +
                          str(xdim) + '\t' +
                          str(ydim) + '\t' +
                          figureLabel + '\t' +
                          COPYRIGHT + '\t' +
                          CAPTION + '\n')

        fpImagePaneFile.write(pixID + '\t' + '\n')

        line = fpPixFile.readline()

    return 0


#
# Main
#
openFiles()
process()
closeFiles()

sys.exit(0)
