#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: J80502-10.5.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To translate 10.5 image files into input files
#	for the gxdimageload.py program.
#
# Requirements Satisfied by This Program:
#
# Usage:
#
#	J80502-10.5.py
#
# Envvars:
#
# Inputs:
#
#	probe_table.txt, a tab-delimited file in the format:
#		field 1: Human Gene
#		field 2: Mouse Gene
#               field 3: MGI Marker Accession ID
#		field 4: Clone Name
#		field 5: Clone Origin
#		field 6: Clone Acc ID
#		field 7: Clone Mapping
#		field 8: Clone MGI ID
#		field 9: Clone Library ID
#		field 10: Clone Library Name
#
#       pix10.5.txt, a tab-delimited file in the format:
#		field 1: Image File Name
#		field 2: PIX ID (####)
#
#	E10.5_In_situ.txt, a tab-delimited file in the format:
#               field 1: Vial #
#               field 2: Mouse Gene Symbol
#               field 3: MGI Marker Accession ID
#               field 4: Human Gene
#               field 5-16: Tissues
#		field 17: Image file name
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
inProbeFile = ''	# file descriptor

datadir = os.environ['GXDIMGLOADDATADIR']
pixeldatadir = os.environ['PIXELDBDATA']

inInSituFileName = datadir + '/tr4800/data/E10.5_In_situ.txt'
inPixFileName = datadir + '/pix10.5.txt'
inProbeFileName = datadir + '/tr4800/data/probe_table.txt'
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
paneLabel = ''
multiProbeNote = 'Several probes were used to assay for this gene with repeatable results.  This image is attached to each assay.'

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
    global diagFile, inInSituFile, inPixFile, inProbeFile, imageFile, paneFile
 
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
        inProbeFile = open(inProbeFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inProbeFileName)

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

    # marker ID:probe ID mapping
    probeDict = {}
    for line in inProbeFile.readlines():
	tokens = string.split(line[:-1], TAB)
	mgiID = tokens[2]
	probeID = tokens[7]

	if len(mgiID) == 0:
	    continue

	key = mgiID
	value = probeID
	if not probeDict.has_key(key):
	    probeDict[key] = []
        probeDict[key].append(value)

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
	    vial = tokens[0]
	    mouseGene = tokens[1]
	    accID = tokens[2]
	    humanGene = tokens[3]
	    results = tokens[4:15]
	    imageFileName = tokens[15]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	if len(mouseGene) == 0:
	    continue

	if len(imageFileName) == 0:
	    continue

	if not pixelDict.has_key(imageFileName):
	    print 'Cannot Find Image (%d): %s\n' % (lineNum, imageFileName)
	    continue

	# get x and y image dimensions

	(xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[imageFileName] + jpegSuffix)

	# if the gene is assayed using more than one probe, use the special note
        if len(probeDict[accID]) > 1:
	    imageNote = multiProbeNote
        else:
	    imageNote = ''

	imageFile.write(reference + TAB + \
	    pixelDict[imageFileName] + TAB + \
	    str(xdim) + TAB + \
	    str(ydim) + TAB + \
	    imageFileName + TAB + \
	    copyrightNote + TAB + \
	    imageNote + CRT)

	paneFile.write(pixelDict[imageFileName] + TAB + \
	    paneLabel + CRT)

    # end of "for line in inPixFile.readlines():"

#
# Main
#

init()
process()
exit(0)

# $Log$
# Revision 1.6  2003/07/18 16:17:28  lec
# TR 4800
#
# Revision 1.5  2003/07/17 18:30:14  lec
# TR 4800
#
# Revision 1.4  2003/07/17 17:44:53  lec
# TR 4800
#
# Revision 1.3  2003/07/17 17:25:34  lec
# TR 4800
#
# Revision 1.2  2003/07/17 13:20:17  lec
# TR 4800
#
# Revision 1.1  2003/07/16 19:41:10  lec
# TR 4800
#
#
