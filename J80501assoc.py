#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: J80501assoc.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load Image Associations for J:80501 InSitus
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
#       pix80501.txt, a tab-delimited file in the format:
#               field 1: Image File Name
#               field 2: PIX ID (####)
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
import assoclib

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

inInSituFileName = datadir + '/tr5154/9.5_dpc_in_situ_results.txt'
inPixFileName = datadir + '/pix80501.txt'

# output files

outAssocFile = ''	# file descriptor

assocTable = 'GXD_InSituResultImage'

outAssocFileName = datadir + '/' + assocTable + '.bcp'

diagFileName = ''	# diagnostic file name
errorFileName = ''	# error file name
passwordFileName = ''	# password file name

mode = ''		# processing mode (load, preview)

reference = 'J:80501'
createdBy = os.environ['CREATEDBY']

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
	    paperID = tokens[0]
	    cloneID = tokens[1]
	    mgiCloneID = tokens[2]
	    mouseGene = tokens[3]
	    accID = tokens[4]
	    results = tokens[5:24]
	    imageFileNames = tokens[24:]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	if len(mouseGene) == 0:
	    continue

	for imageFileName in imageFileNames:

	    i = string.strip(imageFileName)

	    if len(i) == 0:
	        continue

	    if not pixelDict.has_key(i):
	        print 'Cannot Find Image (%d): %s\n' % (lineNum, i)
	        continue

            imagePaneKey = assoclib.verifyImage(pixelDict[i], lineNum)

            if imagePaneKey == 0:
                # set error flag to true
                error = 1

            # if errors, continue to next record
            if error:
                continue

            # if no errors, process

	    # for each Assay of the Gene
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
# Revision 1.4  2003/09/25 13:38:36  lec
# TR 5154
#
# Revision 1.3  2003/09/24 14:32:43  lec
# TR 5154
#
# Revision 1.2  2003/09/22 11:24:37  lec
# TR 5154
#
# Revision 1.1  2003/09/19 19:52:07  lec
# TR 5154
#
#
