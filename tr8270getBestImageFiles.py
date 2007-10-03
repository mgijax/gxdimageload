#!/usr/local/bin/python

#
#  tr8270getBestImageFiles.py
###########################################################################
#
#  Purpose:
#
#      This script will create a list of file names that are defined as
#      "best images".
#
#  Usage:
#
#      tr8270getBestImageFiles.py
#
#  Env Vars:
#
#      BEST_IMAGE_FILE
#      IMAGE_LIST_FILE
#      PIXELDB_FILES
#
#  Inputs:
#
#      ImageList.txt - Tab-delimited fields:
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
#      BestImage.txt - Tab-delimited fields:
#
#          1) Marker MGI ID
#          2) Marker Symbol
#          3) Analysis ID
#          4) Probe ID
#          5) Probe Name
#          6) Specimen ID
#          7) Accession Number
#          8) Best image slide/section for structure 1
#          .
#          .  Repeat best image for each of the 100 structures.
#          .
#          .  NOTE: Not all structures have a best image.
#          .
#          107) Best image slide/section for structure 100
#
#  Outputs:
#
#      PixelDBFileList.txt - This file contains a list of image files that
#                            have been defined as "best images".
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
#  08/27/2007  DBM  Initial development
#
###########################################################################

import sys
import os
import string
import re

#
#  CONSTANTS
#
ANALYSIS_ID_INDEX = 2
FIRST_BEST_IMAGE_INDEX = 7
FIRST_SLIDE_SECTION_INDEX = 8

#
#  GLOBALS
#
bestImageFile = os.environ['BEST_IMAGE_FILE']
imageListFile = os.environ['IMAGE_LIST_FILE']
outFile = os.environ['PIXELDB_FILES']


#
# Purpose: Create a dictionary for looking up the slide/section numbers for
#          an analysis ID. The information for the dictionary is read from a
#          file that contains all the best image data.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variable
# Throws: Nothing
#
def buildBestImageLookup ():
    global bestImageLookup

    #
    # Open the input file.
    #
    try:
        fpBestImage = open(bestImageFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + bestImageFile + '\n')
        sys.exit(1)

    #
    # Build a dictionary of best image slide/section numbers for each
    # analysis ID, keyed by analysis ID.
    #
    bestImageLookup = {}
    line = fpBestImage.readline()
    line = fpBestImage.readline()
    while line:
        tokens = re.split('\t', line[:-1])
        imageList = []

        #
        # Build a list of unique slide/section numbers for the current line
        # of the input file.
        #
        for t in tokens[FIRST_BEST_IMAGE_INDEX:]:
            if t != '' and imageList.count(t) == 0:
                imageList.append(t)

        #
        # Sort the list and add it to the dictionary.
        #
        imageList.sort()
        bestImageLookup[tokens[ANALYSIS_ID_INDEX]] = imageList

        line = fpBestImage.readline()

    fpBestImage.close()

    return


#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpImageList, fpOut

    #
    # Open the input file.
    #
    try:
        fpImageList = open(imageListFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + imageListFile + '\n')
        sys.exit(1)

    #
    # Open the output file.
    #
    try:
        fpOut = open(outFile, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + outFile + '\n')
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
    fpOut.close()

    return


#
# Purpose: Create a list of best image files to be added to Pixel DB.
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
        analysisID = tokens[ANALYSIS_ID_INDEX]

        #
        # Create an index into the token list that points to the first set
        # of image data.  Work through each set of image data to find any
        # that are in the best image list.
        #
        i = FIRST_SLIDE_SECTION_INDEX
        while i < len(tokens):
            slideSection = tokens[i]
            filename = tokens[i+1]

            #
            # If the slide/section number is in the best image list for
            # the current analysis ID, write the file name to the output
            # file because it is one that is needed for pixel DB.
            #
            imageList = bestImageLookup[analysisID]
            if imageList.count(slideSection) > 0:
                fpOut.write(filename + '\n')

            #
            # Advance the index to the next set of image data.
            #
            i += 4

        line = fpImageList.readline()

    return 0


#
# Main
#
buildBestImageLookup()
openFiles()
process()
closeFiles()

sys.exit(0)
