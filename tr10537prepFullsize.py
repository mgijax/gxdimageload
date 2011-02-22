#!/usr/local/bin/python

#
#  tr10537prepFullsize.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the fullsize images.
#
#  Usage:
#
#      tr10537prepFullsize.py
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
#          1) Reference ("J:162220")
#          2) Fullsize image key (blank)
#          3) Image class ("Expression")
#          4) Pixel DB accession number (numeric part)
#          5) X dimension of the image
#          6) Y dimension of the image
#          7) Figure label
#          8) Copyright note
#          9) Caption note
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
CAPTION = '''This image was contributed directly to GXD by the Brain Gene Expression Map (BGEM) database. High resolution images for this gene can be accessed via the BGEM link at the bottom of this page.'''
COPYRIGHT = '''This image is from Magdaleno S, PLoS Biol 2006 Apr;4(4):e86, an open-access article distributed under the terms of the Creative Commons Attribution License. The data in BGEM are available without restriction. BGEM images may be incorporated into grant proposals, scientific presentations, and manuscripts by citing the BGEM URL (http://www.stjudebgem.org) and this publication. BGEM is a free resource that represents a new avenue for information exchange that will accelerate understanding of the nervous system.'''

IMAGE_CLASS = 'Expression'
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
        # (e.g. g00001_sj_g27_049_e11.jpg) and the pix ID that represents the
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
                          IMAGE_CLASS + '\t' +
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
