#!/usr/local/bin/python

#
# Program: tr7982assoc.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load additional Image Associations for J:101679 InSitus
#
#	GXD_InSituResultImage
#
# Requirements Satisfied by This Program:
#
# Usage:
#	tr7982assoc.py
#
# Envvars:
#
# Inputs:
#
#       Result_Image.txt, a tab-delimited file in the format:
#		field 1: Result key
#		field 2: Image File Names
#
# Outputs:
#
#       BCP files:
#
#       GXD_InSituResultImage.bcp	Image Association records
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
import db
import mgi_utils
import assoclib

#globals

#
# from configuration file
#
mode = os.environ['LOADMODE']
createdBy = os.environ['CREATEDBY']
user = os.environ['MGD_DBUSER']
passwordFileName = os.environ['MGD_DBPASSWORDFILE']
datadir = os.environ['DATADIR']	# directory which contains the data files
logdir = os.environ['LOGDIR']   # directory that contains the log files

DEBUG = 0		# if 0, not in debug mode
TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
bcpdelim = TAB		# bcp file delimiter

bcpon = 1		# can the bcp files be bcp-ed into the database?  default is yes.

diagFile = ''		# diagnostic file descriptor
errorFile = ''		# error file descriptor

# input files

inImageFile = ''	# file descriptor
inPixFile = ''		# file descriptor

inImageFileName = datadir + '/Result_Image.txt'
inPixFileName = datadir + '/pix7982.txt'

# output files

outAssocFile = ''	# file descriptor

assocTable = 'GXD_InSituResultImage'

outAssocFileName = datadir + '/' + assocTable + '.bcp'

diagFileName = ''	# diagnostic file name
errorFileName = ''	# error file name

cdate = mgi_utils.date('%m/%d/%Y')	# current date

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
#          exits if files cannot be opened
# Throws: nothing

def init():
    global diagFile, errorFile, errorFileName, diagFileName
    global inPixFile, inImageFile
    global outAssocFile
 
    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFileName)
 
    fdate = mgi_utils.date('%m%d%Y')	# current date
    head, tail = os.path.split(sys.argv[0])
    diagFileName = logdir + '/' + tail + '.' + fdate + '.diagnostics'
    errorFileName = logdir + '/' + tail + '.' + fdate + '.error'

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
        inPixFile = open(inPixFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inPixFileName)

    # Output Files

    try:
        outAssocFile = open(outAssocFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outAssocFileName)

    # Log all SQL
    db.set_sqlLogFunction(db.sqlLogAll)

    # Set Log File Descriptor
    db.set_sqlLogFD(diagFile)

    diagFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))
    diagFile.write('Server: %s\n' % (db.get_sqlServer()))
    diagFile.write('Database: %s\n' % (db.get_sqlDatabase()))

    errorFile.write('Start Date/Time: %s\n\n' % (mgi_utils.date()))

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

# Purpose:  BCPs the data into the database
# Returns:  nothing
# Assumes:  nothing
# Effects:  BCPs the data into the database
# Throws:   nothing

def bcpFiles():

    if DEBUG or not bcpon:
        return

    outAssocFile.close()

    bcpI = 'cat %s | bcp %s..' % (passwordFileName, db.get_sqlDatabase())
    bcpII = '-c -t\"%s' % (bcpdelim) + '" -S%s -U%s' % (db.get_sqlServer(), db.get_sqlUser())

    bcp1 = '%s%s in %s %s' % (bcpI, assocTable, outAssocFileName, bcpII)
    diagFile.write('%s\n' % bcp1)
    os.system(bcp1)

    # update statistics
    db.sql('update statistics %s' % (assocTable), None)

    return

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  verifies and processes each line in the input file
# Throws:   nothing

def process():

    pixelDict = assoclib.readPixelFile(inPixFile)

    for line in inImageFile.readlines():
	tokens = string.split(line[:-1], TAB)
	resultKey = tokens[0]
	imgFileName = tokens[1]

	if imgFileName == '.jpg':
	    continue

	if not pixelDict.has_key(imgFileName):
	    print 'Cannot Find Image in Pixel Dict: %s\n' % (imgFileName)
	    continue

        imagePaneKey = assoclib.verifyImage(pixelDict[imgFileName], 0, errorFile)

        if imagePaneKey == 0:
            # set error flag to true
	    print 'Cannot Find Image Pane Key: %s\n' % (imgFileName)
            continue

        # if no errors, process

	outAssocFile.write(str(resultKey) + TAB + \
	            str(imagePaneKey) + TAB + \
	            cdate + TAB + cdate + CRT)

    #	end of "for line in inImageFile.readlines():"

    bcpFiles()
    return

#
# Main
#

init()
verifyMode()
process()
exit(0)

