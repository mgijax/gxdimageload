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

datadir = os.environ['GXDIMGLOADDATADIR']
pixeldatadir = os.environ['PIXELDBDATA']

inInSituFileName = datadir + '/tr4800/data/E10.5_In_situ.txt'
inPixFileName = datadir + '/pix10.5.txt'
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
multImageNote = 'Several probes were used to assay for this gene with repeatable results.  This image is attached to each assay.'

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

# Purpose:  determines a Marker has been Assayed using more than one Probe
# Returns:  1 if the Marker has been Assayed using more than one Probe
# 	    0 if the Marker has not been Assayed using more than one Probe
# Assumes:  nothing
# Effects:  nothing
# Throws:   nothing

def isMultiProbe(accID):

    results = db.sql('select a._Assay_key ' + \
	'from GXD_Assay a, GXD_ProbePrep pp, PRB_Probe p, BIB_Acc_View b, MRK_Acc_View ma ' + \
	'where a.createdBy = "%s" ' % (createdBy) + \
	'and a._AssayType_key = %s ' % (assayType) + \
	'and a._Refs_key = b._Object_key ' + \
	'and b.accID = "%s" ' % (reference) + \
	'and a._Marker_key = ma._Object_key ' + \
	'and ma.accID = "%s" ' % (accID) + \
	'and a._ProbePrep_key = pp._ProbePrep_key ' + \
	'and pp._Probe_key = p._Probe_key ' + \
	'and p.DNAType != "primer"', 'auto')

    if len(results) > 1:
	return 1
    else:
	return 0

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

    # For each line in the assay input file

    assay = 0

    for line in inInSituFile.readlines():

        # Split the line into tokens
        tokens = string.split(line[:-1], TAB)

	# skip first line (header)
	if assay == 0:
	    assay = assay + 1
	    continue

	# else process an actual data line

        try:
	    vial = tokens[0]
	    mouseGene = tokens[1]
	    accID = tokens[2]
	    humanGene = tokens[3]
	    results = tokens[4:14]
	    imageFileName = tokens[15]

        except:
            print 'Invalid Line (%d): %s\n' % (assay, line)

	assay = assay + 1

	if len(mouseGene) == 0:
	    continue

	if not pixelDict.has_key(imageFileName):
	    print 'Cannot Find Image (%d): %s\n' % (assay, imageFileName)
	    continue

	if isMultiProbe(accID) == 1:
	    imageNote = multImageNote
	else:
	    imageNote = ''

	(xdim, ydim) = jpeginfo.getDimensions(pixeldatadir + '/' + pixelDict[imageFileName] + jpegSuffix)

	imageFile.write(reference + TAB + \
	    pixelDict[imageFileName] + TAB + \
	    str(xdim) + TAB + \
	    str(ydim) + TAB + \
	    imageFileName + TAB + \
	    copyrightNote + TAB + \
	    imageNote + CRT)

	paneFile.write(pixelDict[imageFileName] + TAB + \
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
#
