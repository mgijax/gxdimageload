#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: J80502-14.5assoc.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load Image Associations for J:80502/14.5 InSitus
#
#	GXD_InSituResultImage
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
#       pix14.5.txt, a tab-delimited file in the format:
#               field 1: Image File Name
#               field 2: PIX ID (####)
#
#       14.5_In_situ.txt, a tab-delimited file in the format:
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
import getopt
import db
import mgi_utils
import accessionlib

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

inInSituFile = ''	# file descriptor
inPixFile = ''		# file descriptor

inInSituFileName = datadir + '/tr4800/data/14.5_In_situ.txt'
inPixFileName = datadir + '/pix14.5.txt'

# output files

outAssocFile = ''	# file descriptor

assocTable = 'GXD_InSituResultImage'

outAssocFileName = datadir + '/' + assocTable + '.bcp'

diagFileName = ''	# diagnostic file name
errorFileName = ''	# error file name
passwordFileName = ''	# password file name

mode = ''		# processing mode (load, preview)

reference = 'J:80502'
createdBy = os.environ['CREATEDBY']
pixPrefix = 'PIX:'
pixMgiType = 'Image'

# dictionaries to cache data for quicker lookup
imageDict = {}

cdate = mgi_utils.date('%m/%d/%Y')	# current date

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
    global diagFile, errorFile, errorFileName, diagFileName, passwordFileName
    global inInSituFile, inPixFile
    global mode
    global outAssocFile
 
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
        inInSituFile = open(inInSituFileName, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inInSituFileName)

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
    diagFile.write('Server: %s\n' % (server))
    diagFile.write('Database: %s\n' % (database))
    diagFile.write('User: %s\n' % (user))

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

# Purpose:  verifies the pix ID
# Returns:  the primary key of the image pane or 0 if invalid
# Assumes:  nothing
# Effects:  verifies that the Image Pane exists by checking the imageDict
#	dictionary for the pix ID or the database.
#	writes to the error file if the Image Pane is invalid.
#	adds the Pix ID/Key to the global imageDict dictionary if the
#	Image is valid.
# Throws:

def verifyImage(
    pixID,          # pix accession ID; PIX:#### (string)
    lineNum	  # line number (integer)
    ):

    global imageDict

    pixID = pixPrefix + pixID

    if imageDict.has_key(pixID):
        imagePaneKey = imageDict[pixID]
    else:
        imageKey = accessionlib.get_Object_key(pixID, pixMgiType)
        if imageKey is None:
            errorFile.write('Invalid Reference (%d): %s\n' % (lineNum, pixID))
            imageKey = 0
	    imagePaneKey = 0
        else:
	    results = db.sql('select _ImagePane_key from IMG_ImagePane ' + \
		'where _Image_key = %s' % (imageKey), 'auto')
	    imagePaneKey = results[0]['_ImagePane_key']
            imageDict[pixID] = imagePaneKey

    return imagePaneKey

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
    truncateDB = 'dump transaction %s with truncate_only' % (db.get_sqlDatabase())

    bcp1 = '%s%s in %s %s' % (bcpI, assocTable, outAssocFileName, bcpII)
    diagFile.write('%s\n' % bcp1)
    os.system(bcp1)
    db.sql(truncateDB, None)

    # update statistics
    db.sql('update statistics %s' % (assocTable), None)

    return

# Purpose:  processes data
# Returns:  nothing
# Assumes:  nothing
# Effects:  verifies and processes each line in the input file
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

	error = 0

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
            results = tokens[7:50]
	    imageFileName1 = tokens[50]
	    imageFileName2 = tokens[51]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	if len(mouseGene) == 0:
	    continue

	for img in [imageFileName1, imageFileName2]:

	    if len(img) == 0:
		continue

	    if not pixelDict.has_key(img):
	        print 'Cannot Find Image (%d): %s\n' % (lineNum, img)
	        continue

            imagePaneKey = verifyImage(pixelDict[img], lineNum)

            if imagePaneKey == 0:
                # set error flag to true
                error = 1

            # if errors, continue to next record
            if error:
                continue

            # if no errors, process

	    # for each 14.5 Assay of the Gene
	    #    for each Specimen of each Assay
	    #        for each Result of each Specimen
	    #            associate the Image Pane with the Result

	    results = db.sql('select i._Result_key ' + \
		    'from BIB_Acc_View ba, MRK_Acc_View ma, GXD_Assay a, GXD_Specimen s, GXD_InSituResult i ' + \
		    'where ba.accID = "%s" ' % (reference) + \
		    'and ma.accID = "%s" ' % (accID) + \
		    'and ba._Object_key = a._Refs_key ' + \
		    'and ma._Object_key = a._Marker_key ' + \
		    'and a._Assay_key = s._Assay_key ' + \
		    'and s.specimenLabel like "%14.5%" ' + \
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

#
# $Log$
# Revision 1.4  2003/07/17 18:30:15  lec
# TR 4800
#
# Revision 1.3  2003/07/17 17:44:54  lec
# TR 4800
#
# Revision 1.2  2003/07/17 17:25:35  lec
# TR 4800
#
# Revision 1.1  2003/07/17 15:05:16  lec
# TR 4800
#
#
