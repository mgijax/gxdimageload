#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: J80501.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate J:80501 image files into input files
#	for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	J80501.py
#
# Envvars:
#
# Inputs:
#
#       pix80501.txt, a tab-delimited file in the format:
#		field 1: Image File Name
#		field 2: PIX ID (####)
#
#	9.5_dpc_in_situ_results.txt, a tab-delimited file in the format:
#               field 1: Paper ID
#		field 2: Clone ID
#		field 3: MGI clone ID
#		field 4: MGI gene symbol
#		field 5: MGI gene ID
#		field 6: overall expression
#		field 7-25: expression
#		field 26-28: image file names
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

inInSituFile = ''	# file descriptor
inPixFile = ''		# file descriptor

datadir = os.environ['GXDIMGLOADDATADIR']
pixeldatadir = os.environ['PIXELDBDATA']

inInSituFileName = datadir + '/tr5154/9.5_dpc_in_situ_results.txt'
inPixFileName = datadir + '/pix80501.txt'
imageFileName = datadir + '/image.txt'
paneFileName = datadir + '/imagepane.txt'
imageFile = ''
paneFile = ''
diagFile = ''		# diagnostic file descriptor
diagFileName = ''	# diagnostic file name
passwordFileName = ''	# password file name

# constants
jpegSuffix = '.jpg'
reference = 'J:80501'
assayType = '1'		# InSitu Assay
createdBy = os.environ['CREATEDBY']
copyrightNote = 'Reprinted by permission from <A HREF="http://www.nature.com/">Nature</A> (Gitton et al, Nature 2002 Dec 5;420(6915):586-590) copyright (2002) Macmillan Publishers Ltd.'
fieldType = 'Bright field'
paneLabel = ''
imageNote = ''

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
    global diagFile, inInSituFile, inPixFile, imageFile, paneFile
 
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
        inInSituFile = open(inInSituFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inInSituFileName)

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
	pixFileName = tokens[0]
	pixID = tokens[1]
	key = pixFileName
	value = pixID
	pixelDict[key] = value

    # For each line in the input file

    lineNum = 0

    for line in inInSituFile.readlines():

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# skip first line (header)
	if lineNum == 0:
	    lineNum = lineNum + 1
	    continue

	# else process an actual data line

        try:
	    paperID = tokens[0]
	    cloneID = tokens[1]
	    mgiCloneID = tokens[2]
	    mouseGene = tokens[3]
	    accID = tokens[4]
	    results = tokens[5:24]
	    imageFileNames = tokens[25:27]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	if len(mouseGene) == 0:
	    continue

	if len(imageFileNames) == 0:
	    continue

	for imageFileName in imageFileNames:

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
	      imageFileName + TAB + \
	      copyrightNote + TAB + \
	      imageNote + CRT)

	  paneFile.write(pixelDict[i] + TAB + \
	      fieldType + TAB + \
	      paneLabel + CRT)

    # end of "for line in inPixFile.readlines():"

#
# Main
#

init()
process()
exit(0)

# $Log$
# Revision 1.1  2003/09/19 19:28:58  lec
# TR 5154
#
#
