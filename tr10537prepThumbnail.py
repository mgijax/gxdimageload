#!/usr/local/bin/python

#
#  tr10537prepThumbnail.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the thumbnail images.
#
#  Usage:
#
#      tr10537prepThumbnail.py
#
#  Env Vars:
#
#      PIXELDBDATA
#      PIX_THUMBNAIL
#      IMAGE_THUMBNAIL
#      IMAGEPANE_THUMBNAIL
#      REFERENCE
#
#  Inputs:
#
#      Pix_Thumbnail.txt - Tab-delimited fields:
#
#          1) File name of the thumbnail image that has been added to pixel DB
#          2) Accession number from pixel DB (numeric part)
#
#  Outputs:
#
#      image_Thumbnail.txt - Tab-delimited fields:
#
#          1) Reference ("J:162220")
#          2) Fullsize image key (from corresponding fullsize image)
#          3) Image class ("Expression")
#          4) Pixel DB accession number (numeric part)
#          5) X dimension of the image
#          6) Y dimension of the image
#          7) Figure label
#          8) Copyright note (blank)
#          9) Caption note (blank)
#
#      imagepane_Thumbnail.txt - This file will be empty because there are no
#                                image panes for the thumbnail images.  It is
#                                only created because the GXD image load
#                                expects it.
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
import db
import re
import jpeginfo

#
#  CONSTANTS
#
CAPTION = ''
COPYRIGHT = ''

IMAGE_CLASS = 'Expression'
FULLSIZE_IMAGE_TYPE_KEY = 1072158

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_THUMBNAIL']
imageFile = os.environ['IMAGE_THUMBNAIL']
imagePaneFile = os.environ['IMAGEPANE_THUMBNAIL']
jNumber = os.environ['REFERENCE']


#
# Purpose: Create a dictionary for looking up the fullsize image key for
#          a given figure label.
# Returns: Nothing
# Assumes: The fullsize images have already been loaded
# Effects: Sets global variable
# Throws: Nothing
#
def buildImageKeyLookup ():
    global imageKeyLookup

    results = db.sql('select _Object_key ' + \
                     'from ACC_Accession ' + \
                     'where accID = "%s" and ' % (jNumber) + \
                           '_LogicalDB_key = 1 and ' + \
                           '_MGIType_key = 1', 'auto')
    referenceKey = results[0]['_Object_key']

    results = db.sql('select _Image_key, figureLabel ' + \
                     'from IMG_Image ' + \
                     'where _Refs_key = %d and ' % (referenceKey) + \
                           '_ImageType_key = %d' % (FULLSIZE_IMAGE_TYPE_KEY), 'auto')

    imageKeyLookup = {}
    for r in results:
        imageKeyLookup[r['figureLabel']] = r['_Image_key']

    return


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


        #
        # There should be a fullsize image key for the figure label.
        #
        if imageKeyLookup.has_key(figureLabel):
            imageKey = imageKeyLookup[figureLabel]
        else:
            sys.stderr.write('Fullsize image missing for figure label: ' + figureLabel + '\n')
            sys.exit(1)

        fpImageFile.write(jNumber + '\t' +
                          str(imageKey) + '\t' +
                          IMAGE_CLASS + '\t' +
                          pixID + '\t' +
                          str(xdim) + '\t' +
                          str(ydim) + '\t' +
                          figureLabel + '\t' +
                          COPYRIGHT + '\t' +
                          CAPTION + '\n')

        line = fpPixFile.readline()

    return 0


#
# Main
#
buildImageKeyLookup()
openFiles()
process()
closeFiles()

sys.exit(0)
