#!/usr/local/bin/python

#
# Program: tr8145.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To create input files for the gxdimageload.py program.
#	from full-size stubs for journal "Proc Natl Acad Sci U S A".
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

import sys
import os
import string
import db
import mgi_utils
import assoclib

#globals

TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
NULL = ''

datadir = os.environ['DATADIR']

outImageFileName = datadir + '/image.txt'
outPaneFileName = datadir + '/imagepane.txt'
outErrorFileName = datadir + '/image.error'
outImageFile = None
outPaneFile = None
outErrorFile = None

# constants
copyrightNote = ''
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
    global outImageFile, outPaneFile, outErrorFile
 
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

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  writes data to output files
# Throws:   nothing

def process():

    # For each GXD full size image, create a stub for the Thumbnail

    # retrieve full size images where thumbnail is null
    # and journal = "Proc Natl Acad Sci U S A"

    results = db.sql('select i._Image_key, i.jnumID, i.figureLabel ' + \
        	'from IMG_Image_View i, BIB_Refs r ' + \
        	'where i._ImageType_key = 1072158 ' + \
        	'and i._ThumbnailImage_key is null ' + \
		'and i._Refs_key = r._Refs_key ' + \
		'and r.journal = "Proc Natl Acad Sci U S A" ' + \
		'order by i.jnum', 'auto')

    for r in results:

	outImageFile.write(r['jnumID'] + TAB + \
	          str(r['_Image_key']) + TAB + \
	          TAB + \
	          TAB + \
	          TAB + \
	          r['figureLabel'] + TAB + \
	          copyrightNote + TAB + \
	          imageNote + CRT)

    # end of "for line in fp.readlines():"

#
# Main
#

init()
process()
exit(0)

