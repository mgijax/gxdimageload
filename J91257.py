#!/usr/local/bin/python

# $Header$

#
# Program: J91257.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate J:91257 image files into input files
#	for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	J91257.py
#
# Envvars:
#
# Inputs:
#
#       pix91257.txt, a tab-delimited file in the format:
#		field 1: Image File Name
#		field 2: PIX ID (####)
#
#       E13.5_In_Situ_Coding_Table.txt, a tab-delimited file in the format:
#               field 1: Gene Symbol
#               field 2: MTF# (ignore)
#               field 3: Image file name
#               field 4: Informativity (ignore)
#               field 5: E-expression
#               field 6: E-specificity
#               field 7: E-CNS
#               field 8-19: remaining expression
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
import getopt
import mgi_utils
import jpeginfo

#globals

TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
NULL = ''

inInSituFile1 = ''	# file descriptor
inPixFile = ''		# file descriptor

datadir = os.environ['GXDIMGLOADDATADIR']
pixeldatadir = os.environ['PIXELDBDATA']

inInSituFile1Name = datadir + '/tr6118/E13.5_In_Situ_Coding_Table.txt'
inPixFileName = datadir + '/pix91257.txt'
imageFileName = datadir + '/image.txt'
paneFileName = datadir + '/imagepane.txt'
imageFile = ''
paneFile = ''

# constants
jpegSuffix = '.jpg'
reference = 'J:91257'
assayType = '1'		# InSitu Assay
createdBy = os.environ['CREATEDBY']
copyrightNote = 'Reprinted by permission from <A HREF="http://www.nature.com/">Nature</A> (Gitton et al, Nature 2002 Dec 5;420(6915):586-590) copyright (2002) Macmillan Publishers Ltd.'
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
 
    sys.exit(status)
 
# Purpose: initialize
# Returns: nothing
# Assumes: nothing
# Effects: initializes global variables
#          exits if files cannot be opened
# Throws: nothing

def init():
    global inInSituFile1, inPixFile, imageFile, paneFile
 
    try:
        inInSituFile1 = open(inInSituFile1Name, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inInSituFile1Name)

    try:
        inPixFile = open(inPixFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inPixFileName)

    try:
        imageFile = open(imageFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % imageFileName)

    try:
        paneFile = open(paneFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % paneFileName)

    return

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  writes data to output files
# Throws:   nothing

def process():

    # pixFileName:pixID mapping
    pixelDict = {}
    for line in inPixFile.readlines():
	tokens = string.split(line[:-1], TAB)
	pixFileName = tokens[0]
	pixID = tokens[1]
	key = pixFileName
	value = pixID
	pixelDict[key] = value

    # For each line in the input file

    lineNum = 0

    for line in inInSituFile1.readlines():

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# skip first line (header)
	if lineNum == 0:
	    lineNum = lineNum + 1
	    continue

	# else process an actual data line

        try:
#            mouseGene = tokens[0]
#            mtf = tokens[1]
	    imageFileName = tokens[2]
#               field 4: Informativity (ignore)
#            eExpression = tokens[4]
#            eSpecificity = tokens[5]
#            eCNS = tokens[6]
#            eResults = tokens[7:19]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	if len(imageFileName) == 0:
	    continue

	i = string.strip(imageFileName)

	if len(i) == 0:
	    continue

	if not pixelDict.has_key(i):
	    print 'Cannot Find Image (%d): %s\n' % (lineNum, i)
	    continue

	  # get x and y image dimensions

	(xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[i] + jpegSuffix)

	imageFile.write(reference + TAB + \
	      pixelDict[i] + TAB + \
	      str(xdim) + TAB + \
	      str(ydim) + TAB + \
	      i + TAB + \
	      copyrightNote + TAB + \
	      imageNote + CRT)

	paneFile.write(pixelDict[i] + TAB + paneLabel + CRT)

    # end of "for line in inPixFile.readlines():"

#
# Main
#

init()
process()
exit(0)

# $Log$
#
