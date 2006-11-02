#!/usr/local/bin/python

#
# Program: tr8002.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate GXD thumbnail image files into input files for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	tr8002.py
#
# Envvars:
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
# Exit Codes:
#
# Assumes:
#
# Bugs:
#
# Implementation:
#

import sys
import os
import string
import db
import mgi_utils
import jpeginfo
import assoclib

#globals

TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
NULL = ''

inImage = ''	# file descriptor
inPixFile = ''	# file descriptor

datadir = os.environ['DATADIR']
pixeldatadir = os.environ['PIXELDBDATA']
inPixFileName = os.environ['PIXFILE']

outImageFileName = datadir + '/image.txt'
outPaneFileName = datadir + '/imagepane.txt'
outErrorFileName = datadir + '/image.error'
outImageFile = None
outPaneFile = None
outErrorFile = None
pixelDict = {}

# constants
copyrightNote = ''
paneLabel = ''
imageNote = ''

# Purpose: prints error message and exits
# Returns: nothing
# Assumes: nothing
# Effects: exits with exit status
# Throws: nothing

def exit(
    status,          # numeric exit status (integer)
    message = None   # exit message (string)
    ):

    if message is not None:
        sys.stderr.write('\n' + str(message) + '\n')
 
    try:
	inPixFile.close()
	outImageFile.close()
	outPaneFile.close()
	outErrorFile.close()

    except:
	pass

    sys.exit(status)
 
# Purpose: initialize
# Returns: nothing
# Assumes: nothing
# Effects: initializes global variables
#          exits if files cannot be opened
# Throws: nothing

def init():
    global inPixFile, outImageFile, outPaneFile, outErrorFile, pixelDict
 
    try:
        inPixFile = open(inPixFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inPixFileName)

    try:
        outImageFile = open(outImageFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outImageFileName)

    try:
        outPaneFile = open(outPaneFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outPaneFileName)

    try:
        outErrorFile = open(outErrorFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outErrorFileName)

    pixelDict = assoclib.readPixelFile(inPixFile)
    inPixFile.close()

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  writes data to output files
# Throws:   nothing

def process():

    # For each GXD full size image, create a stub for the Thumbnail

    # retrieve full size images where thumbnail is null

    results = db.sql('select a.numericPart, i._Image_key, i.jnumID, i.figureLabel ' + \
        	'from ACC_Accession a, IMG_Image_View i ' + \
        	'where a._LogicalDB_key = 19 ' + \
        	'and a._Object_key = i._Image_key ' + \
        	'and i._ImageType_key = 1072158 ' + \
        	'and i._ThumbnailImage_key is null', 'auto')

    for r in results:

	pixID = str(r['numericPart']) + '.jpg'

	if not pixelDict.has_key(pixID):
	    outErrorFile.write('Cannot Find Thumbnail Image: %s\n' % (pixID))
	    continue

	# get x and y image dimensions

	(xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[pixID] + '.jpg')

	outImageFile.write(r['jnumID'] + TAB + \
	          str(r['_Image_key']) + TAB + \
	          pixelDict[pixID] + TAB + \
	          str(xdim) + TAB + \
	          str(ydim) + TAB + \
	          r['figureLabel'] + TAB + \
	          copyrightNote + TAB + \
	          imageNote + CRT)

#	don't create any panes for these images
#	outPaneFile.write(pixelDict[pixID] + TAB + paneLabel + CRT)

    # end of "for line in fp.readlines():"

#
# Main
#

init()
process()
exit(0)

