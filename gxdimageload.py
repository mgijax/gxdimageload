#!/usr/local/bin/python

#
# Program: gxdimageload.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load new Images into IMG Structures
#
# Requirements Satisfied by This Program:
#
# Usage:
#	gxdimageload.py
#
# Envvars:
#
# Inputs:
#
#       Image file, a tab-delimited file in the format:
#		field 1: Reference (J:####)
#		field 2: Full Size Image Key (can be blank)
#		field 3: Image Class (_Vocab_key = 83)
#		field 4: PIX ID (PIX:#####)
#		field 5: X Dimension
#		field 6: Y Dimension
#               field 7: Figure Label
#               field 8: Copyright Note
#               field 9: Image Note
#
#	Image Pane file, a tab-delimited file in the format:
#		field 1: PIX ID (PIX:####)
#		field 2: Pane Label
#
# Outputs:
#
#       BCP files:
#
#       IMG_Image.bcp			master Image records
#	IMG_ImagePane.bcp		Image Pane records
#       IMG_ACC_Accession.bcp           Accession records
#
#	IMG_Copyright.in		input file for noteload
#	IMG_Caption.in			input file for noteload
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
# History
#
# 11/24/2010	lec
#	- TR10033/image class
#
# 05/19/2010	lec
#	- TR10220/updating the Thumbnail key for the Fullsize record
#	- (see TR10161/TRT10159/TR9485 for examples)
#	see bcpFiles...added db.sql() to update the IMG_Image._ThumbnailImage_key
#	after the new fullsize/thumbnail images have been loaded.
#
# 11/01/2006	lec
#	- TR 8002; changes to support bulk loading of thumbnail images
#	  and associations between thumbnails and pre-existing full size images.
#

import sys
import os
import string
import db
import mgi_utils
import loadlib

#globals

#
# from configuration file
#
mode = os.environ['IMAGELOADMODE']
createdBy = os.environ['CREATEDBY']
user = os.environ['MGD_DBUSER']
passwordFileName = os.environ['MGD_DBPASSWORDFILE']

datadir = os.environ['IMAGELOADDATADIR']
outCopyrightFileName = os.environ['COPYRIGHTFILE']
outCaptionFileName = os.environ['CAPTIONFILE']

inImageFileName = os.environ['IMAGEFILE']
inPaneFileName = os.environ['IMAGEPANEFILE']

outFileQualifier = os.environ['OUTFILE_QUALIFIER']

DEBUG = 0		# if 0, not in debug mode
TAB = '\t'		# tab
CRT = '\n'		# carriage return/newline
bcpdelim = TAB		# bcp file delimiter

bcpon = 1		# can the bcp files be bcp-ed into the database?  default is yes.

diagFile = ''		# diagnostic file descriptor
errorFile = ''		# error file descriptor

# input files

inImageFile = ''         # file descriptor
inPaneFile = ''          # file descriptor

# output files

outImageFile = ''	# file descriptor
outCopyrightFile = ''	# file descriptor
outCaptionFile = ''	# file descriptor
outPaneFile = ''	# file descriptor
outAccFile = ''         # file descriptor

imageTable = 'IMG_Image'
paneTable = 'IMG_ImagePane'
accTable = 'ACC_Accession'

outImageFileName = datadir + '/' + imageTable + '_' + outFileQualifier + '.bcp'
outPaneFileName = datadir + '/' + paneTable + '_' + outFileQualifier + '.bcp'
outAccFileName = datadir + '/' + accTable + '_' + outFileQualifier + '.bcp'

diagFileName = ''	# diagnostic file name
errorFileName = ''	# error file name

# primary keys

imageKey = 0            # IMG_Image._Image_key
paneKey = 0		# IMG_ImagePane._ImagePane_key
accKey = 0              # ACC_Accession._Accession_key
mgiKey = 0              # ACC_AccessionMax.maxNumericPart
createdByKey = ''

# accession constants

imageMgiTypeKey = '9'	# Image
imageVocabClassKey = '83'	# Image Class Vocabulary
gxdMgiTypeKey = '8'	# MGI Type for Image records
mgiPrefix = "MGI:"	# Prefix for MGI accession ID
accLogicalDBKey = '1'	# Logical DB Key for MGI accession ID
accPrivate = '0'	# Private status for MGI accession ID (false)
accPreferred = '1'	# Preferred status MGI accession ID (true)
pixPrefix = 'PIX:'	# Prefix for PIX
pixLogicalDBKey = '19'	# Logical DB Key for PIX ID
pixPrivate = '1'	# Private status for PIX ID (true)

FSimageTypeKey = 1072158	# Full Size Image Type key
TNimageTypeKey = 1072159	# Thumbnail Image Type key

# dictionaries to cache data for quicker lookup

imagePix = {}

loaddate = loadlib.loaddate

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
    global diagFile, errorFile, inputFile, errorFileName, diagFileName
    global outImageFile, outCopyrightFile, outCaptionFile, outPaneFile, outAccFile
    global inImageFile, inPaneFile
    global createdByKey
 
    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFileName)
 
    diagFileName = datadir + '/gxdimageload.diagnostics'
    errorFileName = datadir + '/gxdimageload.error'

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
        outPaneFile = open(outPaneFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outPaneFileName)

    try:
        outAccFile = open(outAccFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outAccFileName)

    try:
        outCaptionFile = open(outCaptionFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outCaptionFileName)

    try:
        outCopyrightFile = open(outCopyrightFileName, 'w')
    except:
        exit(1, 'Could not open file %s\n' % outCopyrightFileName)

    # Log all SQL
    db.set_sqlLogFunction(db.sqlLogAll)

    # Set Log File Descriptor
    db.set_sqlLogFD(diagFile)

    diagFile.write('Start Date/Time: %s\n' % (mgi_utils.date()))
    diagFile.write('Server: %s\n' % (db.get_sqlServer()))
    diagFile.write('Database: %s\n' % (db.get_sqlDatabase()))

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

    global referenceKey

    if DEBUG or not bcpon:
        return

    outImageFile.close()
    outCopyrightFile.close()
    outCaptionFile.close()
    outPaneFile.close()
    outAccFile.close()

    bcpI = 'cat %s | bcp %s..' % (passwordFileName, db.get_sqlDatabase())
    bcpII = '-c -t\"%s' % (bcpdelim) + '" -S%s -U%s' % (db.get_sqlServer(), db.get_sqlUser())

    bcp1 = '%s%s in %s %s' % (bcpI, imageTable, outImageFileName, bcpII)
    bcp2 = '%s%s in %s %s' % (bcpI, paneTable, outPaneFileName, bcpII)
    bcp3 = '%s%s in %s %s' % (bcpI, accTable, outAccFileName, bcpII)

    for bcpCmd in [bcp1, bcp2, bcp3]:
	diagFile.write('%s\n' % bcpCmd)
	os.system(bcpCmd)

    # attach thumbnail image keys to fullsize images
    # images are determined by reference
    # the fullsize figureLabel = thumbnail figure label
    # within a given reference

    db.sql('''
	select _Image_key, _Refs_key, figureLabel
	into #thumbnail
	from IMG_Image 
	where _Refs_key = %s
	and _ImageType_key = %s
	''' % (referenceKey, TNimageTypeKey), None)

    db.sql('''
	update IMG_Image
	set _ThumbnailImage_key = t._Image_key
	from IMG_Image i, #thumbnail t
	where i._Refs_key = %s
	and i._ImageType_key = %s
	and i._ThumbnailImage_key is null
	and i._Refs_key = t._Refs_key
	and i.figureLabel = t.figureLabel
	''' % (referenceKey, FSimageTypeKey), None)
	
    # update the max Accession ID value
    db.sql('exec ACC_setMax %d' % (recordsProcessed), None)

    # update statistics
    db.sql('update statistics %s' % (imageTable), None)
    db.sql('update statistics %s' % (paneTable), None)

    return

# Purpose:  processes image data
# Returns:  nothing
# Assumes:  nothing
# Effects:  verifies and processes each line in the input file
# Throws:   nothing

def processImageFile():

    global imageKey, accKey, mgiKey
    global imagePix
    global referenceKey

    lineNum = 0
    # For each line in the input file

    for line in inImageFile.readlines():

        error = 0
        lineNum = lineNum + 1

        # Split the line into tokens
        tokens = string.split(line[:-1], '\t')

        try:
	    jnum = tokens[0]
	    fullsizeKey = tokens[1]
	    imageClass = tokens[2]
	    pixID = tokens[3]
	    xdim = tokens[4]
	    ydim = tokens[5]
	    figureLabel = tokens[6]
	    copyrightNote = tokens[7]
	    imageNote = tokens[8]
        except:
            exit(1, 'Invalid Line (%d): %s\n' % (lineNum, line))

        imageClassKey = loadlib.verifyTerm('', imageVocabClassKey, imageClass, lineNum, errorFile)
        if imageClassKey == 0:
            # set error flag to true
            error = 1

        referenceKey = loadlib.verifyReference(jnum, lineNum, errorFile)
        if referenceKey == 0:
            # set error flag to true
            error = 1

        # if errors, continue to next record
        if error:
            continue

        # if no errors, process

	if fullsizeKey != '':
	    imageTypeKey = TNimageTypeKey
	    updateFullSizeImage = 1
        else:
	    imageTypeKey = FSimageTypeKey
	    updateFullSizeImage = 0

        outImageFile.write(str(imageKey) + TAB + \
	    str(gxdMgiTypeKey) + TAB + \
	    str(imageClassKey) + TAB + \
	    str(imageTypeKey) + TAB + \
	    str(referenceKey) + TAB + \
	    TAB + \
	    xdim + TAB + \
	    ydim + TAB + \
	    figureLabel + TAB + \
	    str(createdByKey) + TAB + \
	    str(createdByKey) + TAB + \
	    loaddate + TAB + loaddate + CRT)

        # MGI Accession ID for the image

	mgiAccID = mgiPrefix + str(mgiKey)

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

	if len(pixID) > 0:
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

	# Copyrights

	if len(copyrightNote) > 0:
            outCopyrightFile.write(mgiAccID + TAB + copyrightNote + CRT)

	# Notes

	if len(imageNote) > 0:
            outCaptionFile.write(mgiAccID + TAB + imageNote + CRT)

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

	#print str(paneKey)
	#print str(imagePix[pixID])

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

