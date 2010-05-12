#!/usr/local/bin/python

#
# Program: tr10161fullsize.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To create input files for the gxdimageload.py program.
#	from full-size of TR10161.
#
# Input:
#
#       ImageStubs.txt, tab-delimited file in the format:
#               field 1: Reference (J:####)
#               field 2: Full Size Image Key (can be blank)
#               field 3: PIX ID (PIX:#####)
#               field 4: X Dimension
#               field 5: Y Dimension
#               field 6: Figure Label
#               field 7: Copyright Note
#               field 8: Image Note
#               field 9: file name
#
#	PIX_FULLSIZE, tab-delimited list of full size
#		field 1: file name
#		field 2: pix id
#
#	PIX_THUMBNAIL, tab-delimited list of full size
#		field 1: file name
#		field 2: pix id
#
# Outputs:
#
#       4 tab-delimited files:
#
#	image_Fullsize.txt
#	imagepane_Fullsize.txt
#	image_Thumbnail.txt
#	imagepane_Thumbnail.txt
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

FULLSIZE_IMAGE_KEY = ''
THUMBNAIL_IMAGE_KEY = '1072158'

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
imageListFile = os.environ['IMAGE_LIST_FIG_FILE']

pixFile1 = os.environ['PIX_FULLSIZE']
pixFile2 = os.environ['PIX_THUMBNAIL']

imageFile1 = os.environ['IMAGE_FULLSIZE']
imagePaneFile1 = os.environ['IMAGEPANE_FULLSIZE']
imageFile2 = os.environ['IMAGE_THUMBNAIL']
imagePaneFile2 = os.environ['IMAGEPANE_THUMBNAIL']

pixelDict1 = {}
pixelDictr2 = {}

#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpImageList
    global fpImageFile1, fpImagePaneFile1, pixelDict1
    global fpImageFile2, fpImagePaneFile2, pixelDict2

    #
    # Open the input file.
    #
    try:
        fpImageList = open(imageListFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + imageListFile + '\n')
        sys.exit(1)

    try:
        fpPixFile1 = open(pixFile1, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + pixFile1 + '\n')
        sys.exit(1)

    try:
        fpPixFile2 = open(pixFile2, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + pixFile2 + '\n')
        sys.exit(1)

    #
    # Open the output files.
    #
    try:
        fpImageFile1 = open(imageFile1, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imageFile1 + '\n')
        sys.exit(1)

    try:
        fpImagePaneFile1 = open(imagePaneFile1, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imagePaneFile1 + '\n')
        sys.exit(1)

    try:
        fpImageFile2 = open(imageFile2, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imageFile2 + '\n')
        sys.exit(1)

    try:
        fpImagePaneFile2 = open(imagePaneFile2, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imagePaneFile2 + '\n')
        sys.exit(1)

    pixelDict1 = assoclib.readPixelFile(fpPixFile1)
    pixelDict2 = assoclib.readPixelFile(fpPixFile2)

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
    fpImageFile1.close()
    fpImagePaneFile1.close()
    fpImageFile2.close()
    fpImagePaneFile2.close()

    return


#
# Purpose: Create the image and image pane output files for each pixel DB
#          image that is being added.
# Returns: 0 if successful, 1 for an error
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
#               field 1: Reference (J:####)
#               field 2: Full Size Image Key (can be blank)
#               field 3: PIX ID (PIX:#####)
#               field 4: X Dimension
#               field 5: Y Dimension
#               field 6: Figure Label
#               field 7: Copyright Note
#               field 8: Image Note
#               field 9: file name

def process ():

    #
    # Search through each line of the image list file.
    #
    lineNum = 0
    for line in fpImageList.readlines():

	lineNum = lineNum + 1

        tokens = string.split(line[:-1], '\t')
        jNumber =  tokens[0]
        #fullsizeImageKey =  tokens[1]; not used
        #pixID =  tokens[2]; see below
        #xdim =  tokens[3]; see below
        #ydim =  tokens[4]; see below
        figureLabel =  tokens[5]
        copyrightNote =  tokens[6]
        captionNote =  tokens[7]
	fullsizeFile = tokens[8]

	filename = fullsizeFile

	if not pixelDict1.has_key(filename):
        	print 'Cannot find filename: ' + filename + '\n'
		continue
		
        pixID = pixelDict1[filename]

        #
        # Get the X an Y dimensions of the image file.
        #
        (xdim, ydim) = jpeginfo.getDimensions(pixelDBDir + '/' + pixID + '.jpg')

        fpImageFile1.write(jNumber + '\t' +
                           FULLSIZE_IMAGE_KEY + '\t' +
                           pixID + '\t' +
                           str(xdim) + '\t' +
                           str(ydim) + '\t' +
                           figureLabel + '\t' +
                           copyrightNote + '\t' +
                           captionNote + '\n')

        fpImagePaneFile1.write(pixID + '\t' + '\n')

	if not pixelDict2.has_key(filename):
        	print 'Cannot find filename: ' + filename + '\n'
		continue
		
        pixID = pixelDict2[filename]

        #
        # Get the X an Y dimensions of the image file.
        #
        (xdim, ydim) = jpeginfo.getDimensions(pixelDBDir + '/' + pixID + '.jpg')

        fpImageFile2.write(jNumber + '\t' +
                           THUMBNAIL_IMAGE_KEY + '\t' +
                           pixID + '\t' +
                           str(xdim) + '\t' +
                           str(ydim) + '\t' +
                           figureLabel + '\t' +
                           copyrightNote + '\t' +
                           captionNote + '\n')

        fpImagePaneFile2.write(pixID + '\t' + '\n')

    return 0

#
# Main
#
openFiles()
process()
closeFiles()

sys.exit(0)
