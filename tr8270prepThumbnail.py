#!/usr/local/bin/python

#
#  tr8270prepThumbnail.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the thumbnail images.
#
#  Usage:
#
#      tr8270prepThumbnail.py
#
#  Env Vars:
#
#      PIXELDBDATA
#      PIX_THUMBNAIL
#      IMAGE_LIST_FIG_FILE
#      IMAGE_THUMBNAIL
#      IMAGEPANE_THUMBNAIL
#      REFERENCE
#
#  Inputs:
#
#      ImageListFigLabels.txt - Tab-delimited fields:
#
#          1) Marker MGI ID
#          2) Marker Symbol
#          3) Analysis ID
#          4) Probe ID
#          5) Probe Name
#          6) Specimen ID
#          7) Accession Number
#          8) Set number for image 1
#          9) Slide/section number for image 1
#          10) Image file name for image 1
#          11) Figure label for image 1
#          .
#          .  Repeat image data for a maximum of 24 images.
#          .
#          100) Set number for image 24
#          101) Slide/section number for image 24
#          102) Image file name for image 24
#          103) Figure label for image 24
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
#          1) Reference (J:122989)
#          2) Fullsize image key (from corresponding fullsize image)
#          3) Pixel DB accession number (numeric part)
#          4) X dimension of the image
#          5) Y dimension of the image
#          6) Figure label
#          7) Copyright note (blank)
#          8) Caption note (blank)
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
#
#  Modification History:
#
#  Date        SE   Change Description
#  ----------  ---  -------------------------------------------------------
#
#  08/29/2007  DBM  Initial development
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

FIRST_IMAGE_FILE_INDEX = 9

CAPTION = ''
COPYRIGHT = ''

FULLSIZE_IMAGE_TYPE_KEY = 1072158

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_THUMBNAIL']
imageListFile = os.environ['IMAGE_LIST_FIG_FILE']
imageFile = os.environ['IMAGE_THUMBNAIL']
imagePaneFile = os.environ['IMAGEPANE_THUMBNAIL']
jNumber = os.environ['REFERENCE']


#
# Purpose: Create a dictionary for looking up the pix ID for an image file
#          name. The information for the dictionary is read from a file
#          that contains list of images that are being added to pixel DB.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variable
# Throws: Nothing
#
def buildPixIDLookup ():
    global pixIDLookup

    #
    # Open the input file.
    #
    try:
        fpPixFile = open(pixFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + pixFile + '\n')
        sys.exit(1)

    #
    # Build a dictionary of pix IDs for each image file name, keyed by
    # image file name.
    #
    pixIDLookup = {}
    line = fpPixFile.readline()
    while line:
        tokens = re.split('\t', line[:-1])
        pixIDLookup[tokens[0]] = tokens[1]
        line = fpPixFile.readline()

    fpPixFile.close()

    return


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
    global fpImageList, fpImageFile, fpImagePaneFile

    #
    # Open the input file.
    #
    try:
        fpImageList = open(imageListFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + imageListFile + '\n')
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
    line = fpImageList.readline()
    line = fpImageList.readline()
    while line:
        tokens = re.split('\t', line[:-1])

        #
        # Create an index into the token list that points to the first image
        # file.  Work through each image file in the input line.
        #
        i = FIRST_IMAGE_FILE_INDEX
        while i < len(tokens):
            filename =  tokens[i]
            figureLabel = tokens[i+1]

            #
            # If there is no image file, advance the index to the next one.
            #
            if filename == '':
                i += 4
                continue

            #
            # Put an extra "0" in the filename from the input line to make
            # it match the actual name of the file.  For example, the name
            # "MH00000099_0001B.jpg" should be "MH00000099_00001B.jpg".
            #
            filename =  re.sub('_', '_0', filename, 1)

            #
            # If the image file is in the dictionary of pixel DB images, it is
            # one that needs to be written to the output file.
            #
            if pixIDLookup.has_key(filename):
                pixID = pixIDLookup[filename]

                #
                # There should be a fullsize image key for the figure label.
                #
                if imageKeyLookup.has_key(figureLabel):
                    imageKey = imageKeyLookup[figureLabel]
                else:
                    sys.stderr.write('Fullsize image missing for figure label: ' + figureLabel + '\n')
                    sys.exit(1)

                #
                # Get the X an Y dimensions of the image file.
                #
                (xdim, ydim) = jpeginfo.getDimensions(pixelDBDir + '/' +
                                                      pixID + '.jpg')

                fpImageFile.write(jNumber + '\t' +
                                  str(imageKey) + '\t' +
                                  pixID + '\t' +
                                  str(xdim) + '\t' +
                                  str(ydim) + '\t' +
                                  figureLabel + '\t' +
                                  COPYRIGHT + '\t' +
                                  CAPTION + '\n')

            #
            # Advance the index to the next image file.
            #
            i += 4

        line = fpImageList.readline()

    return 0


#
# Main
#
buildPixIDLookup()
buildImageKeyLookup()
openFiles()
process()
closeFiles()

sys.exit(0)