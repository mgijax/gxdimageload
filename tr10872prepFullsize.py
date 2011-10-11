#!/usr/local/bin/python

#
# Program: tr10872.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To create input files for the gxdimageload.py program.
#	from full-size of TR10872.
#
# Input:
#
#	PIX_FULLSIZE, tab-delimited list of full size
#		field 1: file name
#		field 2: pix id
#
#       J143778stubs.txt, tab-delimited file in the format:
#               field 0: J:143778
#               field 1: Figure Label/Image ID
#               field 2: Copyright Note
#               field 3: Image Note
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

COPYRIGHT = '''Questions regarding this image or its use in publications should be directed to J. Rossant at E-mail: janet.rossant@sickkids.ca.'''

FULLSIZE_IMAGE_KEY = ''

IMAGE_CLASS = 'Expression'

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_FULLSIZE']
imageListFile = os.environ['PIXELDB_FILES']
imageFile = os.environ['IMAGE_FULLSIZE']
imagePaneFile = os.environ['IMAGEPANE_FULLSIZE']
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
        filename = tokens[1] + '.jpg'
	figureLabel = tokens[1]
	copyright = tokens[2]
	imageNote = tokens[3]

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
			  IMAGE_CLASS + '\t' +
                          pixID + '\t' +
                          str(xdim) + '\t' +
                          str(ydim) + '\t' +
                          figureLabel + '\t' +
                          COPYRIGHT + '\t' +
                          imageNote + '\n')

        fpImagePaneFile.write(pixID + '\t' + '\n')

    return 0

#
# Main
#
openFiles()
process()
closeFiles()

sys.exit(0)
