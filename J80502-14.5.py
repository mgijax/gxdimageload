#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: J80502-14.5.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate 14.5 image files into input files
#	for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	J80502-14.5.py
#
# Envvars:
#
# Inputs:
#
#       pix14.5.txt, a tab-delimited file in the format:
#		field 1: Image File Name
#		field 2: PIX ID (####)
#
#       14.5_In_Situ.txt, a tab-delimited file in the format:
#               field 1: Human Gene
#               field 2: Mouse Gene Symbol
#               field 3: MGI Marker Accession ID
#               field 4: ISH_number
#               field 5: Specimen
#               field 6: Tissue Quality
#               field 7: Overall Expression
#               field 8-50: Results
#               field 51: Image 1
#               field 52: Image 2
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

inInSituFileName = datadir + '/tr4800/data/14.5_In_situ.txt'
inPixFileName = datadir + '/pix14.5.txt'
imageFileName = datadir + '/image.txt'
paneFileName = datadir + '/imagepane.txt'
imageFile = ''
paneFile = ''
diagFile = ''		# diagnostic file descriptor
diagFileName = ''	# diagnostic file name
passwordFileName = ''	# password file name

# constants
jpegSuffix = '.jpg'
reference = 'J:80502'
assayType = '1'		# InSitu Assay
createdBy = os.environ['CREATEDBY']
copyrightNote = 'This image is from Reymond A, Nature 2002 Dec 5;420(6915):582-6, and is displayed with the permission of <A HREF="http://www.nature.com/">The Nature Publishing Group</A> who owns the Copyright.'
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
            humanGene = tokens[0]
            mouseGene = tokens[1]
            accID = string.strip(tokens[2])
            ishNumber = tokens[3]
            specimen = tokens[4]
            tissueQuality = tokens[5]
            overallExpression = tokens[6]
            results = tokens[7:49]
	    imageFileName1 = tokens[50]
	    imageFileName2 = tokens[51]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	if len(mouseGene) == 0:
	    continue

	for img in [imageFileName1, imageFileName2]:

	    if not pixelDict.has_key(img):
	        print 'Cannot Find Image (%d): %s\n' % (lineNum, img)
	        continue

	    (xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[img] + jpegSuffix)

	    imageFile.write(reference + TAB + \
	        pixelDict[img] + TAB + \
	        str(xdim) + TAB + \
	        str(ydim) + TAB + \
	        img + TAB + \
	        copyrightNote + TAB + \
	        imageNote + CRT)

	    paneFile.write(pixelDict[img] + TAB + \
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
# Revision 1.1  2003/07/17 13:20:10  lec
# new
#
#
