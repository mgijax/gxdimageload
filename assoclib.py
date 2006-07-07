#!/usr/local/bin/python

#
# Program: assoclib.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	Some common routines for association loads
#
# Requirements Satisfied by This Program:
#
# Usage:
#
# Envvars:
#
# Inputs:
#
# Outputs:
#
# Exit Codes:
#
# Assumes:
#
#	That no one else is adding records to the database.
#
# Bugs:
#
# Implementation:
#

import sys
import os
import string
import db
import accessionlib

#globals

TAB = '\t'
pixPrefix = 'PIX:'
pixMgiType = 'Image'
imageDict = {}	 # dictionary of pix id/image pane key

# Purpose:  verifies the pix ID
# Returns:  the primary key of the image pane or 0 if invalid
# Assumes:  nothing
# Effects:  verifies that the Image Pane exists by checking the imageDict
#	dictionary for the pix ID or the database.
#	writes to the error file if the Image Pane is invalid.
#	adds the Pix ID/Key to the global imageDict dictionary if the
#	Image is valid.
# Throws:

def verifyImage(
    pixID,          # pix accession ID; PIX:#### (string)
    lineNum,	    # line number (integer)
    errorFile       # the error file to write to
    ):

    global imageDict

    pixID = pixPrefix + pixID

    if imageDict.has_key(pixID):
        imagePaneKey = imageDict[pixID]
    else:
        imageKey = accessionlib.get_Object_key(pixID, pixMgiType)
        if imageKey is None:
	    if errorFile is not None:
                errorFile.write('Invalid Reference (%d): %s\n' % (lineNum, pixID))
	    imagePaneKey = 0
        else:
	    results = db.sql('select _ImagePane_key from IMG_ImagePane where _Image_key = %s' % (imageKey), 'auto')
	    imagePaneKey = results[0]['_ImagePane_key']
            imageDict[pixID] = imagePaneKey

    return imagePaneKey

def readPixelFile(fp):

    pixelDict = {}

    for line in fp.readlines():
	tokens = string.split(line[:-1], TAB)
	pixFileName = tokens[0]
	pixID = tokens[1]
	pixelDict[pixFileName] = pixID

    return pixelDict

