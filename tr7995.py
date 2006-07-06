#!/usr/local/bin/python

#
# Program: J103446.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate J:103446 image files into input files
#	for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	J103446.py
#
# Envvars:
#
# Inputs:
#
#       IMAGES.txt, a tab-delimited file in the format:
#		field 1: Image Folder in TR directory
#		field 2: Image File Names
#		field 3: Speciman label
#		field 4: Figure Label
#		field 5: Caption
#		field 6: Age (ignore)
#
# Outputs:
#
#       2 tab-delimited files:
#
#	image.txt
#	imagepane.txt
#	
#       Error file
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
import mgi_utils
import jpeginfo

#globals

TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
NULL = ''

inImage = ''	# file descriptor
inPixFile = ''	# file descriptor

datadir = os.environ['DATADIR']
pixeldatadir = os.environ['PIXELDBDATA']

inImageName = datadir + '/IMAGES.txt'

inPixFileName = datadir + '/pix103446.txt'
outImageFileName = datadir + '/image.txt'
outPaneFileName = datadir + '/imagepane.txt'
outImageFile = ''
outPaneFile = ''
pixelDict = {}

# constants
reference = 'J:103446'
copyrightNote = 'This image was contributed directly to GXD by the authors through the Mahone Center for Neuro-Oncology Funcational Genomic Atlas of the Mouse Brain database at http://mahoney.chip.org/mahoney/RBP/.  Questions regarding this image or its use in publications should be directed to P.M. Silver at E-mail:  pamela_silver@hms.harvard.edu.'
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
	inImage.close()
	inPixFile.close()
	outImageFile.close()
	outPaneFile.close()

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
    global inImage, inPixFile, outImageFile, outPaneFile, pixelDict
 
    try:
        inImage = open(inImageName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inImageName)

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

    # pixFileName:pixID mapping
    pixelDict = {}
    for line in inPixFile.readlines():
	tokens = string.split(line[:-1], TAB)
	pixFileName = tokens[0]
	pixID = tokens[1]
	key = pixFileName
	value = pixID
	pixelDict[key] = value
    inPixFile.close()

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  writes data to output files
# Throws:   nothing

def process(fp):

    # For each line in the input file

    lineNum = 0

    for line in fp.readlines():

	lineNum = lineNum + 1

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# skip first line (header)
	if lineNum == 1:
	    continue

	# else process an actual data line

	imageFile = tokens[1]
	imageFileLabel = tokens[3]
	imageNote = tokens[4]

	if not pixelDict.has_key(imageFile):
	    print 'Cannot Find Image (%d): %s\n' % (lineNum, imageFile)
	    continue

	# get x and y image dimensions

	(xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[imageFile] + '.jpg')

	outImageFile.write(reference + TAB + \
	          pixelDict[imageFile] + TAB + \
	          str(xdim) + TAB + \
	          str(ydim) + TAB + \
	          imageFileLabel + TAB + \
	          copyrightNote + TAB + \
	          imageNote + CRT)

	outPaneFile.write(pixelDict[imageFile] + TAB + paneLabel + CRT)

    # end of "for line in fp.readlines():"

#
# Main
#

init()
process(inImage)
exit(0)

