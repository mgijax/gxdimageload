#!/usr/local/bin/python

# $Header$
# $Name$

#
# Program: J91257assoc.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#	To load Image Associations for J:91257 InSitus
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
#       pix91257.txt, a tab-delimited file in the format:
#               field 1: Image File Name
#               field 2: PIX ID (####)
#
#       E13.5_In_Situ_Coding_Table.txt, a tab-delimited file in the format:
#               field 1: Gene Symbol
#               field 2: MTF# (ignore)
#               field 3: Image file name
#               field 4: Informativity (ignore)
#               field 5: E-expression
#               field 6: E-specificity
#               field 7: E-CNS
#               field 8-19: remaining expression
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
import loadlib
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

inInSituFile1 = ''	# file descriptor
inInSituFile2 = ''	# file descriptor
inInSituFile3 = ''	# file descriptor
inPixFile = ''		# file descriptor

inInSituFile1Name = datadir + '/tr6118/E13.5_In_Situ_Coding_Table.txt'
inInSituFile2Name = datadir + '/tr6118/P0_In_Situ_Coding_Table.txt'
inInSituFile3Name = datadir + '/tr6118/WM_Coding_Table.txt'
inPixFileName = datadir + '/pix91257.txt'

# output files

outAssocFile = ''	# file descriptor

assocTable = 'GXD_InSituResultImage'

outAssocFileName = datadir + '/' + assocTable + '.bcp'

diagFileName = ''	# diagnostic file name
errorFileName = ''	# error file name
passwordFileName = ''	# password file name

mode = ''		# processing mode (load, preview)

reference = 'J:91257'
createdBy = os.environ['CREATEDBY']
refKey = ''

pixelDict = {}   # dictionary of pix file name/pix id
mgiProbe = {}	 # dictionary of Probe Name/Probe key

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
	inInSituFile1.close()
	inInSituFile2.close()
	inInSituFile3.close()
	inPixFile.close()
	outAssocFile.close()
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
    global inInSituFile1, inInSituFile2, inInSituFile3, inPixFile, pixelDict
    global mode, mgiProbe, refKey
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
        inInSituFile1 = open(inInSituFile1Name, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inInSituFile1Name)

    try:
        inInSituFile2 = open(inInSituFile2Name, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inInSituFile2Name)

    try:
        inInSituFile3 = open(inInSituFile3Name, 'r')
    except:
        exit(1, 'Could not open file %s\n' % inInSituFile3Name)

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

    results = db.sql('select p.name, p._Probe_key from PRB_Probe p where p.name like "MTF#%"', 'auto')
    for r in results:
        mgiProbe[r['name']] = r['_Probe_key']

    refKey = loadlib.verifyReference(reference, 0, errorFile)
    pixelDict = assoclib.readPixelFile(inPixFile)

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

def process(fp, age):

    # For each line in the input file

    lineNum = 0

    for line in fp.readlines():

	error = 0

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# skip first line (header)
	if lineNum == 0:
	    lineNum = lineNum + 1
	    continue

	# else process an actual data line

        try:
            mtf = tokens[1]
	    imageFile = tokens[2]

        except:
            print 'Invalid Line (%d): %s\n' % (lineNum, line)

	lineNum = lineNum + 1

	tokens = string.split(imageFile, '.jpg')
	imageFile = tokens[0]

	if len(imageFile) == 0:
	    continue

	imageFiles = string.split(imageFile, ';')

	for imageFile in imageFiles:

	    if not pixelDict.has_key(imageFile):
	        print 'Cannot Find Image (%d): %s\n' % (lineNum, imageFile)
	        continue

            probeName = 'MTF#' + mtf
	    probeKey = mgiProbe[probeName]
            imagePaneKey = assoclib.verifyImage(pixelDict[imageFile], lineNum, errorFile)

            if imagePaneKey == 0:
                # set error flag to true
                error = 1

            # if errors, continue to next record
            if error:
                continue

            # if no errors, process

	    # for each Assay of the Probe
	    #    for each Specimen of each Assay
	    #        for each Result of each Specimen
	    #            associate the Image Pane with the Result

	    results = db.sql('select i._Result_key ' + \
		        'from GXD_Assay a, GXD_ProbePrep p, GXD_Specimen s, GXD_InSituResult i ' + \
		        'where a._Refs_key = %s ' % (refKey) + \
		        'and a._ProbePrep_key = p._ProbePrep_key ' + \
		        'and p._Probe_key = %s ' % (probeKey) + \
		        'and a._Assay_key = s._Assay_key ' + \
			'and s.age = "%s" ' % (age) + \
		        'and s._Specimen_key = i._Specimen_key', 'auto')

	    for r in results:
	        outAssocFile.write(str(r['_Result_key']) + TAB + \
	                str(imagePaneKey) + TAB + \
	                loaddate + TAB + loaddate + CRT)

    #	end of "for line in fp.readlines():"

    return

#
# Main
#

init()
verifyMode()
process(inInSituFile1, 'embryonic day 13.5')
process(inInSituFile2, 'postnatal newborn')
process(inInSituFile3, 'embryonic day 10.5')
bcpFiles()
exit(0)

#
# $Log$
# Revision 1.6  2004/09/16 16:39:06  lec
# TR 6118
#
# Revision 1.5  2004/09/16 16:27:55  lec
# TR 6118
#
# Revision 1.4  2004/09/16 16:17:51  lec
# TR 6118
#
# Revision 1.3  2004/09/16 13:21:37  lec
# TR 6118
#
# Revision 1.1  2004/09/09 15:18:15  lec
# TR 6118
#
#
