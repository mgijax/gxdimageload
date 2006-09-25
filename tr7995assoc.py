#!/usr/local/bin/python

#
# Program: tr7995assoc.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load additional Image Associations for J:103446 InSitus
#
#	GXD_InSituResultImage
#
# Requirements Satisfied by This Program:
#
# Usage:
#	tr7995assoc.py
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
#	ASSAYS.txt, a tab-delimited file in the format:
#               field 1: MGI Assay ID
#		field 2: Image folder
#		field 3: Image file(s) - "; " delimited
#		field 4-7: ignore
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
passwordFileName = os.environ['MGI_DBPASSWORDFILE']
datadir = os.environ['DATADIR']	# directory which contains the data files
logdir = os.environ['LOGDIR']  # directory which contains the log files

DEBUG = 0		# if 0, not in debug mode
TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
bcpdelim = TAB		# bcp file delimiter

bcpon = 1		# can the bcp files be bcp-ed into the database?  default is yes.

diagFile = ''		# diagnostic file descriptor
errorFile = ''		# error file descriptor

# input files

inAssayFile = ''	# file descriptor
inImageFile = ''	# file descriptor
inPixFile = ''		# file descriptor

inAssayFileName = datadir + '/ASSAYS.txt'
inImageFileName = datadir + '/IMAGES.txt'
inPixFileName = datadir + '/pix103446.txt'

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
#          calls showUsage() if usage error
#          exits if files cannot be opened
# Throws: nothing

def init():
    global diagFile, errorFile, errorFileName, diagFileName
    global inAssayFile, inPixFile, inImageFile
    global outAssocFile
 
    db.useOneConnection(1)
 
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
        inAssayFile = open(inAssayFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inAssayFileName)

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
#    truncateDB = 'dump transaction %s with truncate_only' % (db.get_sqlDatabase())

    bcp1 = '%s%s in %s %s' % (bcpI, assocTable, outAssocFileName, bcpII)
    diagFile.write('%s\n' % bcp1)
    os.system(bcp1)
#    db.sql(truncateDB, None)

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

    imgDict = {}
    for line in inImageFile.readlines():
	tokens = string.split(line[:-1], TAB)
	imgFileName = tokens[1]
	imgSpecimen = tokens[2]
	key = imgFileName
	value = imgSpecimen
	imgDict[key] = value

    # For each line in the input file

    lineNum = 0

    for line in inAssayFile.readlines():

	# skip first line
	if lineNum == 0:
	    lineNum = lineNum + 1
	    continue

	error = 0

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

        try:
	    mgiID = string.strip(tokens[0])
	    imgFileNames = string.split(string.strip(tokens[2]), '; ')
        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	for i in imgFileNames:

	    if not pixelDict.has_key(i):
	        print 'Cannot Find Image in Pixel Dict (%d): %s\n' % (lineNum, i)
		error = 1

	    if not imgDict.has_key(i):
	        print 'Cannot Find Image in Image Dict (%d): %s\n' % (lineNum, i)
		error = 1

            imagePaneKey = assoclib.verifyImage(pixelDict[i], lineNum, errorFile)

            if imagePaneKey == 0:
                # set error flag to true
	        print 'Cannot Find Image Pane Key (%d): %s\n' % (lineNum, i)
                error = 1

	    specimenLabel = imgDict[i]

            # if errors, continue to next record
            if error:
                continue

            # if no errors, process

	    # for each Assay
	    #    for each Specimen of each Assay
	    #        for each Result of each Specimen
	    #            associate the Image Pane with the Result

	    results = db.sql('select i._Result_key ' + \
		    'from GXD_Assay_Acc_View ac, GXD_Assay a, GXD_Specimen s, GXD_InSituResult i ' + \
		    'where ac.accID = "%s" ' % (mgiID) + \
		    'and ac._Object_key = a._Assay_key ' + \
		    'and a._Assay_key = s._Assay_key ' + \
		    'and s.specimenLabel = "%s" ' % (specimenLabel) + \
		    'and s._Specimen_key = i._Specimen_key', 'auto')

	    for r in results:
	        resultKey = r['_Result_key']

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

