#!/usr/local/bin/python

#
#  tr10976prepFullsize.py
###########################################################################
#
#  Purpose:
#
#      This script will create the input files for the GXD image load to
#      load the fullsize images.
#
#  Usage:
#
#      tr10976prepFullsize.py
#
#  Env Vars:
#
#      PIXELDBDATA
#      PIX_FULLSIZE
#      IMAGE_LIST_FIG_FILE
#      IMAGE_FULLSIZE
#      IMAGEPANE_FULLSIZE
#      REFERENCE
#
#  Inputs:
#
# StrengthPattern.txt
#
# 0. MGI ID
# 1. Gene Symbol
# 2. Analysis ID
# 3. Probe ID
# 4. Probe Name
# 5. Specimen ID
# 6. Primer Name
# 7. Forward Primer
# 8. Reverse Primer
# 9. Strain ID
# 10. Strain MGI ID
# 11. Method ID
# 12. Accession Number
#
# 13. Strength
# 14. Pattern
# 15. Best Image
# 16. Image JPG
# 17. Figure Label
# 18. Note 
#
# 19. Strength
# 20. Pattern
# 21. Best Image
# 22. Image JPG
# 23. Figure Label
# 24. Note 
#
# 104 structures
# 6 * 104 = 624
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
#          1) Reference (J:122989)
#          2) Fullsize image key (blank)
#	   3) Image Class (_Vocab_key = 83)
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
# 04/04/2012	lec
#
###########################################################################

import sys
import os
import jpeginfo

#
#  CONSTANTS
#
FIRST_IMAGE_FILE_INDEX = 16

CAPTION = '''This image was constributed directly to GXD by the GenePaint database.  Additional images for this gene and 'virtual microscope' zoom capability for this image can be accessed via the GenePaint link at the bottom of this page.'''

COPYRIGHT = '''Questions regarding this image or its use in publications should be directed to gpscience@mpibpc.mpg.de'''

FULLSIZE_IMAGE_KEY = ''
IMAGE_CLASS = 'Expression'

#
#  GLOBALS
#
pixelDBDir = os.environ['PIXELDBDATA']
pixFile = os.environ['PIX_FULLSIZE']
imageListFile = os.environ['STR_PATT_FILE']
imageFile = os.environ['IMAGE_FULLSIZE']
imagePaneFile = os.environ['IMAGEPANE_FULLSIZE']
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
        tokens = line[:-1].split('\t')
        pixIDLookup[tokens[0]] = tokens[1]
        line = fpPixFile.readline()
    fpPixFile.close()
    #print pixIDLookup

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

    imageLookup = []

    #
    # Search through each line of the image list file.
    #
    line = fpImageList.readline()
    line = fpImageList.readline()
    while line:
        tokens = line[:-1].split('\t')

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
                i += 6
                continue

	    #
	    #  If this image has already be used, skip
	    #
	    if filename in imageLookup:
                i += 6
                continue

            #
            # If the image file is in the dictionary of pixel DB images, it is
            # one that needs to be written to the output file.
            #
            if pixIDLookup.has_key(filename):

                pixID = pixIDLookup[filename]

                #
                # Get the X an Y dimensions of the image file.
                #
                (xdim, ydim) = jpeginfo.getDimensions(pixelDBDir + '/' +
                                                      pixID + '.jpg')

		# for testing...print out the filename
                #fpImageFile.write(filename + '\t')

                fpImageFile.write(jNumber + '\t' +
                                  FULLSIZE_IMAGE_KEY + '\t' +
				  IMAGE_CLASS + '\t' +
                                  pixID + '\t' +
                                  str(xdim) + '\t' +
                                  str(ydim) + '\t' +
                                  figureLabel + '\t' +
                                  COPYRIGHT + '\t' +
                                  CAPTION + '\n')

                fpImagePaneFile.write(pixID + '\t\t' + str(xdim) + '\t' + str(ydim) + '\n')

            #
	    # Add filename to imageLookup
            # Advance the index to the next image file.
            #
	    imageLookup.append(filename)
            i += 6

        line = fpImageList.readline()

    return 0


#
# Main
#
buildPixIDLookup()
openFiles()
process()
closeFiles()

sys.exit(0)
