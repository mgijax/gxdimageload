#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: gxdimageload.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load new Images into IMG Structures
#
#	IMG_Image
#	IMG_ImageNote
#	IMG_ImagePane
#	ACC_Accession
#
# Requirements Satisfied by This Program:
#
# Usage:
#	program.py
#	-S = database server
#	-D = database
#	-U = user
#	-P = password file
#	-M = mode
#
# Envvars:
#
# Inputs:
#
#       Image file, a tab-delimited file in the format:
#		field 1: Reference (J:####)
#		field 2: X Dimension
#		field 3: Y Dimension
#		field 4: PIX ID (PIX:#####)
#               field 5: Figure Label
#               field 6: Copyright Note
#               field 7: Image Note
#
#	Image Pane file, a tab-delimited file in the format:
#		field 1: PIX ID (PIX:####)
#		field 2: Field Type
#		field 3: Pane Label
#
# Outputs:
#
#       BCP files:
#
#       IMG_Image.bcp			master Image records
#	IMG_ImageNote.bcp		Image note records
#	IMG_ImagePane.bcp		Image Pane records
#       ACC_Accession.bcp               Accession records
#
#       Diagnostics file of all input parameters and SQL commands
#       Error file
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
import getopt
import db
import mgi_utils
import accessionlib
import loadlib

#globals

DEBUG = 0		# if 0, not in debug mode
TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
bcpdelim = TAB		# bcp file delimiter

bcpon = 1		# can the bcp files be bcp-ed into the database?  default is yes.

datadir = os.environ['GXDIMGLOADDATADIR']	# directory which contains the data files

diagFile = ''		# diagnostic file descriptor
errorFile = ''		# error file descriptor

# input files

inImageFile = ''         # file descriptor
inPaneFile = ''          # file descriptor

inImageFileName = datadir + '/image.txt'
inPaneFileName = datadir + '/imagepane.txt'

# output files

outImageFile = ''	# file descriptor
outNoteFile = ''	# file descriptor
outPaneFile = ''	# file descriptor
outAccFile = ''         # file descriptor

imageTable = 'IMG_Image'
noteTable = 'IMG_ImageNote'
paneTable = 'IMG_ImagePane'
accTable = 'ACC_Accession'

outImageFileName = datadir + '/' + imageTable + '.bcp'
outNoteFileName = datadir + '/' + noteTable + '.bcp'
outPaneFileName = datadir + '/' + paneTable + '.bcp'
outAccFileName = datadir + '/' + accTable + '.bcp'

diagFileName = ''	# diagnostic file name
errorFileName = ''	# error file name
passwordFileName = ''	# password file name

mode = ''		# processing mode (load, preview)

createdBy = os.environ['CREATEDBY']

# primary keys

imageKey = 0            # IMG_Image._Image_key
paneKey = 0		# IMG_ImagePane._ImagePane_key
accKey = 0              # ACC_Accession._Accession_key
mgiKey = 0              # ACC_AccessionMax.maxNumericPart
createdByKey = ''

# accession constants

imageMgiTypeKey = '9'	# Image
mgiPrefix = "MGI:"	# Prefix for MGI accession ID
accLogicalDBKey = '1'	# Logical DB Key for MGI accession ID
accPrivate = '0'	# Private status for MGI accession ID (false)
accPreferred = '1'	# Preferred status MGI accession ID (true)
pixPrefix = 'PIX:'	# Prefix for PIX
pixLogicalDBKey = '19'	# Logical DB Key for PIX ID
pixPrivate = '1'	# Private status for PIX ID (true)

# dictionaries to cache data for quicker lookup

imagePix = {}

loaddate = loadlib.loaddate

# Purpose: displays correct usage of this program
# Returns: nothing
# Assumes: nothing
# Effects: exits with status of 1
# Throws: nothing
 
def showUsage():
    usage = 'usage: %s -S server\n' % sys.argv[0] + \
        '-D database\n' + \
        '-U user\n' + \
        '-P password file\n' + \
        '-M mode\n'

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
 
    try:
        diagFile.write('\n\nEnd Date/Time: %s\n' % (mgi_utils.date()))
        errorFile.write('\n\nEnd Date/Time: %s\n' % (mgi_utils.date()))
        diagFile.close()
        errorFile.close()
    except:
        pass

    db.useOneConnection(0)
    sys.exit(status)
 
# Purpose: process command line options
# Returns: nothing
# Assumes: nothing
# Effects: initializes global variables
#          calls showUsage() if usage error
#          exits if files cannot be opened
# Throws: nothing

def init():
    global diagFile, errorFile, inputFile, errorFileName, diagFileName, passwordFileName
    global mode, createdByKey
    global outImageFile, outNoteFile, outPaneFile, outAccFile
    global inImageFile, inPaneFile
 
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'S:D:U:P:M:')
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
        elif opt[0] == '-M':
            mode = opt[1]
        else:
            showUsage()

    # User must specify Server, Database, User and Password
    password = string.strip(open(passwordFileName, 'r').readline())
    if server == '' or database == '' or user == '' or password == '' \
	or mode == '':
        showUsage()

    # Initialize db.py DBMS parameters
    db.set_sqlLogin(user, password, server, database)
    db.useOneConnection(1)
 
    fdate = mgi_utils.date('%m%d%Y')	# current date
    diagFileName = sys.argv[0] + '.' + fdate + '.diagnostics'
    errorFileName = sys.argv[0] + '.' + fdate + '.error'

    try:
        diagFile = open(diagFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % diagFileName)
		
    try:
        errorFile = open(errorFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % errorFileName)
		
    # Input Files

    try:
        inImageFile = open(inImageFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inImageFileName)

    try:
        inPaneFile = open(inPaneFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inPaneFileName)

    # Output Files

    try:
        outImageFile = open(outImageFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outImageFileName)

    try:
        outNoteFile = open(outNoteFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outNoteFileName)

    try:
        outPaneFile = open(outPaneFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outPaneFileName)

    try:
        outAccFile = open(outAccFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outAccFileName)

    # Log all SQL
    db.set_sqlLogFunction(db.sqlLogAll)

    # Set Log File Descriptor
    db.set_sqlLogFD(diagFile)

    diagFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))
    diagFile.write('Server: %s\n' % (server))
    diagFile.write('Database: %s\n' % (database))
    diagFile.write('User: %s\n' % (user))

    errorFile.write('Start Date/Time: %s\n\n' % (mgi_utils.date()))

    createdByKey = loadlib.verifyUser(createdBy, 0, errorFile)

    return

# Purpose: verify processing mode
# Returns: nothing
# Assumes: nothing
# Effects: if the processing mode is not valid, exits.
#	   else, sets global variables
# Throws:  nothing

def verifyMode():

    global DEBUG

    if mode == 'preview':
        DEBUG = 1
        bcpon = 0
    elif mode != 'load':
        exit(1, 'Invalid Processing Mode:  %s\n' % (mode))

# Purpose:  sets global primary key variables
# Returns:  nothing
# Assumes:  nothing
# Effects:  sets global primary key variables
# Throws:   nothing

def setPrimaryKeys():

    global imageKey, paneKey, accKey, mgiKey

    results = db.sql('select maxKey = max(_Image_key) + 1 from IMG_Image', 'auto')
    imageKey = results[0]['maxKey']

    results = db.sql('select maxKey = max(_ImagePane_key) + 1 from IMG_ImagePane', 'auto')
    paneKey = results[0]['maxKey']

    results = db.sql('select maxKey = max(_Accession_key) + 1 from ACC_Accession', 'auto')
    accKey = results[0]['maxKey']

    results = db.sql('select maxKey = maxNumericPart + 1 from ACC_AccessionMax ' + \
        'where prefixPart = "%s"' % (mgiPrefix), 'auto')
    mgiKey = results[0]['maxKey']

# Purpose:  BCPs the data into the database
# Returns:  nothing
# Assumes:  nothing
# Effects:  BCPs the data into the database
# Throws:   nothing

def bcpFiles(
   recordsProcessed	# number of records processed (integer)
   ):

    if DEBUG or not bcpon:
        return

    outImageFile.close()
    outNoteFile.close()
    outPaneFile.close()
    outAccFile.close()

    bcpI = 'cat %s | bcp %s..' % (passwordFileName, db.get_sqlDatabase())
    bcpII = '-c -t\"%s' % (bcpdelim) + '" -S%s -U%s' % (db.get_sqlServer(), db.get_sqlUser())
    truncateDB = 'dump transaction %s with truncate_only' % (db.get_sqlDatabase())

    bcp1 = '%s%s in %s %s' % (bcpI, imageTable, outImageFileName, bcpII)
    bcp2 = '%s%s in %s %s' % (bcpI, noteTable, outNoteFileName, bcpII)
    bcp3 = '%s%s in %s %s' % (bcpI, paneTable, outPaneFileName, bcpII)
    bcp4 = '%s%s in %s %s' % (bcpI, accTable, outAccFileName, bcpII)

    for bcpCmd in [bcp1, bcp2, bcp3, bcp4]:
	diagFile.write('%s\n' % bcpCmd)
	os.system(bcpCmd)
	db.sql(truncateDB, None)

    # update the max Accession ID value
    db.sql('exec ACC_setMax %d' % (recordsProcessed), None)

    # update statistics
    db.sql('update statistics %s' % (imageTable), None)
    db.sql('update statistics %s' % (noteTable), None)
    db.sql('update statistics %s' % (paneTable), None)
    db.sql('update statistics %s' % (accTable), None)

    return

# Purpose:  processes image data
# Returns:  nothing
# Assumes:  nothing
# Effects:  verifies and processes each line in the input file
# Throws:   nothing

def processImageFile():

    global imageKey, accKey, mgiKey
    global imagePix

    lineNum = 0
    # For each line in the input file

    for line in inImageFile.readlines():

        error = 0
        lineNum = lineNum + 1

        # Split the line into tokens
        tokens = string.split(line[:-1], '\t')

        try:
	    jnum = tokens[0]
	    pixID = tokens[1]
	    xdim = tokens[2]
	    ydim = tokens[3]
	    figureLabel = tokens[4]
	    copyrightNote = tokens[5]
	    imageNote = tokens[6]
        except:
            exit(1, 'Invalid Line (%d): %s\n' % (lineNum, line))

        referenceKey = loadlib.verifyReference(jnum, lineNum, errorFile)

        if referenceKey == 0:
            # set error flag to true
            error = 1

        # if errors, continue to next record
        if error:
            continue

        # if no errors, process

        outImageFile.write(str(imageKey) + TAB + \
	    str(referenceKey) + TAB + \
	    xdim + TAB + \
	    ydim + TAB + \
	    figureLabel + TAB + \
	    copyrightNote + TAB + \
	    loaddate + TAB + loaddate + CRT)

        # MGI Accession ID for the image

	outAccFile.write(str(accKey) + TAB + \
	    mgiPrefix + str(mgiKey) + TAB + \
	    mgiPrefix + TAB + \
	    str(mgiKey) + TAB + \
	    accLogicalDBKey + TAB + \
	    str(imageKey) + TAB + \
	    imageMgiTypeKey + TAB + \
	    accPrivate + TAB + \
	    accPreferred + TAB + \
	    str(createdByKey) + TAB + \
	    str(createdByKey) + TAB + \
	    loaddate + TAB + loaddate + CRT)

        accKey = accKey + 1
        mgiKey = mgiKey + 1

	outAccFile.write(str(accKey) + TAB + \
	    pixPrefix + str(pixID) + TAB + \
	    pixPrefix + TAB + \
	    str(pixID) + TAB + \
	    pixLogicalDBKey + TAB + \
	    str(imageKey) + TAB + \
	    imageMgiTypeKey + TAB + \
	    pixPrivate + TAB + \
	    accPreferred + TAB + \
	    str(createdByKey) + TAB + \
	    str(createdByKey) + TAB + \
	    loaddate + TAB + loaddate + CRT)

        accKey = accKey + 1

	# Notes

	if len(imageNote) > 0:

            noteSeq = 1
		
            while len(imageNote) > 255:
                outNoteFile.write(str(imageKey) + TAB + str(noteSeq) + TAB + imageNote[:255] + TAB + loaddate + TAB + loaddate + CRT)
                newnote = imageNote[255:]
                imageNote = newnote
                noteSeq = noteSeq + 1

            if len(imageNote) > 0:
                outNoteFile.write(str(imageKey) + TAB + str(noteSeq) + TAB + imageNote[:255] + TAB + loaddate + TAB + loaddate + CRT)

	imagePix[pixID] = imageKey
        imageKey = imageKey + 1

    #	end of "for line in inImageFile.readlines():"

    return lineNum

# Purpose:  processes image pane data
# Returns:  nothing
# Assumes:  nothing
# Effects:  verifies and processes each line in the input file
# Throws:   nothing

def processImagePaneFile():

    global imagePix, paneKey

    lineNum = 0
    # For each line in the input file

    for line in inPaneFile.readlines():

        error = 0
        lineNum = lineNum + 1

        # Split the line into tokens
        tokens = string.split(line[:-1], '\t')

        try:
	    pixID = tokens[0]
	    paneLabel = tokens[1]
        except:
            exit(1, 'Invalid Line (%d): %s\n' % (lineNum, line))

        outPaneFile.write(str(paneKey) + TAB + \
	    str(imagePix[pixID]) + TAB + \
	    mgi_utils.prvalue(paneLabel) + TAB + \
	    loaddate + TAB + loaddate + CRT)

        paneKey = paneKey + 1

    #	end of "for line in inPaneFile.readlines():"

    return lineNum

def process():

    recordsProcessed = processImageFile()
    recordsProcessed = recordsProcessed + processImagePaneFile()
    bcpFiles(recordsProcessed)

#
# Main
#

init()
verifyMode()
setPrimaryKeys()
process()
exit(0)

#
# $Log$
# Revision 1.2  2003/09/24 12:30:44  lec
# TR 5154
#
# Revision 1.1  2003/07/16 19:41:09  lec
# TR 4800
#
#
