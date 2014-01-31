#!/usr/local/bin/python

#
#  tr11471prepFullsize.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the fullsize images.
#
#  Usage:
#
#      tr11471prepFullsize.py
#
#  Env Vars:
#
#      PIXELDB_FILES
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
#      image_loader.txt - Tab-delimited fields:
#
#	   1) Figure label
#	   2) Image Caption Note
#	   3) File name
#
#  Outputs:
#
#      image_Fullsize.txt - Tab-delimited fields:
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
#      imagepane_Fullsize.txt - Tab-delimited fields:
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
CAPTION = ''
COPYRIGHT = '''Questions regarding this image should be directed to the GUDMAP project: gudmap-editors@gudmap.org.  Information about its use in publications can be found at http://www.gudmap.org/About/Usage.html.'''

FULLSIZE_IMAGE_KEY = ''
IMAGECLASS = 'Expression'

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_FULLSIZE']
imageLoad = os.environ['PIXELDB_FILES']
imageFile = os.environ['IMAGE_FULLSIZE']
imagePaneFile = os.environ['IMAGEPANE_FULLSIZE']
jNumber = os.environ['REFERENCE']

imageLookup = {}

#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpPixFile, fpImageLoadFile, fpImageFile, fpImagePaneFile
    global imageLookup

    #
    # Open the input file.
    #
    try:
        fpPixFile = open(pixFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + pixFile + '\n')
        sys.exit(1)

    #
    # Open the image load file.
    #
    try:
        fpImageLoadFile = open(imageLoad, 'r')
    except:
        sys.stderr.write('Cannot open image load file: ' + imageLoad + '\n')
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

    line = fpImageLoadFile.readline()
    while line:
        tokens = string.split(line[:-1], '\t')

	if len(tokens[2]) == 0:
	    key = tokens[0]
	else:
	    key = tokens[2]
	value = tokens
	if not imageLookup.has_key(key):
	    imageLookup[key] = []
	imageLookup[key].append(value)
        line = fpImageLoadFile.readline()
    fpImageLoadFile.close()

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

    figureLabel = None

    #
    # Process each line of the input file.
    #
    counter = 0
    for line in fpPixFile.readlines():

	counter += 1

        #
        # Tokenize the input record and get the original image files name
        # (e.g. euxassay_000001_01.jpg) and the pix ID that represents the
        # new image file name in pixel DB.
        #
        tokens = string.split(line[:-1], '\t')
        filename =  tokens[0]

	if filename.find('GUDMAP') >= 0:
		pixID = ''
        else:
		pixID = tokens[1]

	#
	# tuple of imageLookup
        # The figure label is derived from the image file name by removing
        # the ".jpg" suffix.
	#
	if filename in imageLookup:

	  for x in imageLookup[filename]:

	    #figureLabel = imageLookup[filename][0][0]
	    figureLabel = x[0]
	    figureLabel = figureLabel.replace('.jpg', '')
	    #CAPTION = imageLookup[filename][0][1]
	    CAPTION = x[1]

	    if filename.find('GUDMAP') >= 0:
		xdim = ''
		ydim = ''
	    else:
            	(xdim, ydim) = jpeginfo.getDimensions(pixelDBDir + '/' + pixID + '.jpg')

            fpImageFile.write(jNumber + '\t' +
                              FULLSIZE_IMAGE_KEY + '\t' +
			      IMAGECLASS + '\t' +
                              pixID + '\t' +
                              str(xdim) + '\t' +
                              str(ydim) + '\t' +
                              figureLabel + '\t' +
                              COPYRIGHT + '\t' +
                              CAPTION + '\t\n')

            fpImagePaneFile.write(pixID + '\t\t' + str(xdim) + '\t' + str(ydim) + '\n')

	#else:
	#    print filename

        line = fpPixFile.readline()

    print counter
    return 0


#
# Main
#
openFiles()
process()
closeFiles()

sys.exit(0)
