#!/usr/local/bin/python

#
# Program: tr9458thumbnail.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To create input files for the gxdimageload.py program.
#	from thumbnail of TR9471.
#
# Input:
#
#       J141291stubs.txt, tab-delimited file in the format:
#               field 1: file name
#
#	PIX_THUMBNAIL, tab-delimited list of thumbnail
#		field 1: file name
#		field 2: pix id
#
# Outputs:
#
#       2 tab-delimited files:
#
#	image.txt
#	imagepane.txt
#	
#       1 error file:
#
#	image.error
#

import sys
import os
import string
import db
import mgi_utils
import jpeginfo
import assoclib

#
#  CONSTANTS
#
FIRST_IMAGE_FILE_INDEX = 9

CAPTION = '''This image was provided by the authors as a direct GXD submission. Questions regarding this image or its use in publications should be directed to Dr. Heiko Lickert at E-mail: heiko.lickert@helmholtz-muenchen.de.'''

COPYRIGHT = '''This image is from Tamplin OJ, BMC Genomics 2008;9(1):511, an open-access article, licensee BioMed Central Ltd.'''

FULLSIZE_IMAGE_KEY = '1072158'

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_THUMBNAIL']
imageListFile = os.environ['IMAGE_LIST_FIG_FILE']
imageFile = os.environ['IMAGE_THUMBNAIL']
imagePaneFile = os.environ['IMAGEPANE_THUMBNAIL']
jNumber = os.environ['REFERENCE']
pixelDict = {}

#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpImageList, fpImageFile, fpImagePaneFile, pixelDict

    #
    # Open the input file.
    #
    try:
        fpImageList = open(imageListFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + imageListFile + '\n')
        sys.exit(1)

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

    pixelDict = assoclib.readPixelFile(fpPixFile)

    return


#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def closeFiles ():
    fpImageList.close()
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
    # Search through each line of the image list file.
    #
    lineNum = 0
    for line in fpImageList.readlines():

	lineNum = lineNum + 1

        tokens = string.split(line[:-1], '\t')
        filename =  tokens[0]
        (figureLabel, j) = string.split(filename, '.jpg')

	if not pixelDict.has_key(filename):
        	print 'Cannot find filename: ' + filename + '\n'
		continue
		
        pixID = pixelDict[filename]

        #
        # Get the X an Y dimensions of the image file.
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

    return 0

#
# Main
#
openFiles()
process()
closeFiles()

sys.exit(0)
