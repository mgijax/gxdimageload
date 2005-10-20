#!/usr/local/bin/python

#
# Program: tr7167.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate tr7167 image files into input files
#	for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	tr7167.py
#
# Envvars:
#
# Inputs:
#
#       KuoImages.txt, a tab-delimited file in the format:
#		field 1: Image File Directory
#		field 2: Image File Name
#		field 3: PIX ID (####)
#
#	IMAGES.txt, a tab-delimited file in the format:
#		field 1: Image File Directory
#		field 2: Image File Name
#		field 3: Speciman Label 
#		field 4: Figure Label
#		field 5: Age, ignore
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
import db
import mgi_utils
import jpeginfo

#globals

TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
NULL = ''

inImageFile = ''	# file descriptor
inPixFile = ''		# file descriptor

datadir = os.environ['DATADIR']
pixeldatadir = os.environ['PIXELDBDATA']

inImageFileName = datadir + '/IMAGES.txt'
inPixFileName = datadir + '/KuoImages.txt'
imageFileName = datadir + '/image.txt'
paneFileName = datadir + '/imagepane.txt'

imageFile = ''
paneFile = ''
diagFile = ''		# diagnostic file descriptor
diagFileName = ''	# diagnostic file name
passwordFileName = ''	# password file name

# constants
reference = 'J:93300'
createdBy = os.environ['CREATEDBY']
copyrightNote = 'Questions regarding this image or its use in publications should be directed to C. L. Cepko at E-mail: cepko@genetics.med.harvard.edu.'
paneLabel = ''
imageNote = 'This image was provided by the authors as a direct GXD submission and was not published within the article or as supplementary material.'

# Purpose: displays correct usage of this program
# Returns: nothing
# Assumes: nothing
# Effects: exits with status of 1
# Throws: nothing
 
def showUsage():
    usage = 'usage: %s -S server\n' % sys.argv[0] + \
        '-D database\n' + \
        '-U user\n' + \
        '-P password file\n'

    exit(1, usage)
 
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
 
    db.useOneConnection(0)
    sys.exit(status)
 
# Purpose: initialize
# Returns: nothing
# Assumes: nothing
# Effects: initializes global variables
#          exits if files cannot be opened
# Throws: nothing

def init():
    global diagFile, inImageFile, inPixFile, imageFile, paneFile
 
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'S:D:U:P:')
    except:
        showUsage()
 
    #
    # Set server, database, user, passwords depending on options specified
    #
 
    server = ''
    database = ''
    user = ''
    password = ''
 
    for opt in optlist:
        if opt[0] == '-S':
            server = opt[1]
        elif opt[0] == '-D':
            database = opt[1]
        elif opt[0] == '-U':
            user = opt[1]
        elif opt[0] == '-P':
            passwordFileName = opt[1]
        else:
            showUsage()

    # User must specify Server, Database, User and Password
    password = string.strip(open(passwordFileName, 'r').readline())
    if server == '' or database == '' or user == '' or password == '':
        showUsage()

    # Initialize db.py DBMS parameters
    db.set_sqlLogin(user, password, server, database)
    db.useOneConnection(1)
 
    fdate = mgi_utils.date('%m%d%Y')	# current date
    diagFileName = sys.argv[0] + '.' + fdate + '.diagnostics'

    try:
        diagFile = open(diagFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % diagFileName)
		
    try:
        inImageFile = open(inImageFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inImageFileName)

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

    # Log all SQL
    db.set_sqlLogFunction(db.sqlLogAll)

    # Set Log File Descriptor
    db.set_sqlLogFD(diagFile)

    diagFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))
    diagFile.write('Server: %s\n' % (server))
    diagFile.write('Database: %s\n' % (database))
    diagFile.write('User: %s\n' % (user))

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
	pixFolder = tokens[0]
	pixFileName = tokens[1]
	pixID = tokens[2]
	key = pixFolder + ':' + pixFileName
	value = pixID
	pixelDict[key] = value

    # For each line in the input file

    lineNum = 0

    for line in inImageFile.readlines():

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# process an actual data line

        try:
	    imageFolder = tokens[0]
	    imageFileName = tokens[1]
	    specimenLabel = tokens[2]
	    figureLabel = tokens[3]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	i = imageFolder + ':' + imageFileName
	if not pixelDict.has_key(i):
	    print 'Cannot Find Image (%d): %s\n' % (lineNum, i)
	    continue

	# get x and y image dimensions

	(xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[i] + '.jpg')

	imageFile.write(reference + TAB + \
	     pixelDict[i] + TAB + \
	     str(xdim) + TAB + \
	     str(ydim) + TAB + \
	     figureLabel + TAB + \
	     copyrightNote + TAB + \
	     imageNote + CRT)

	paneFile.write(pixelDict[i] + TAB + paneLabel + CRT)

    # end of "for line in inImageFile.readlines():"

#
# Main
#

init()
process()
exit(0)

