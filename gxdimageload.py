#!/usr/local/bin/python

#
# Program: gxdimageload.py
#
# Original Author: Lori Corbani
#
# Purpose:
#
#       To load new Images into IMG Structures
#
# Requirements Satisfied by This Program:
#
# Usage:
#       gxdimageload.py
#
# Envvars:
#
# Inputs:
#
#       Image file, a tab-delimited file in the format:
#               field 1: Reference (J:####)
#               field 2: Full Size Image Key (can be blank)
#               field 3: Image Class (_Vocab_key = 83)
#               field 4: PIX ID (#####)
#               field 5: X Dimension
#               field 6: Y Dimension
#               field 7: Figure Label
#               field 8: Copyright Note
#               field 9: Image Note
#               field 10: LogicalDB|Image AccID (optional)
#                       where LogicalDB is the ldb of the URL to which to attach the accID
#                       where Image AccID is accID
#
#       Image Pane file, a tab-delimited file in the format:
#               field 1: PIX ID (####)
#               field 2: Pane Label
#               field 3: X Dimension (width)
#               field 4: Y Dimension (heigth)
#
# Outputs:
#
#       BCP files:
#
#       IMG_Image.bcp                   master Image records
#       IMG_ImagePane.bcp               Image Pane records
#       ACC_Accession.bcp (fullsize, thumbnail, images)
#
#       IMG_Copyright.in                input file for noteload
#       IMG_Caption.in                  input file for noteload
#
#       Diagnostics file of all input parameters and SQL commands
#       Error file
#
# Exit Codes:
#
# Assumes:
#
#       That no one else is adding records to the database.
#
# Bugs:
#
# Implementation:
#
# History
#
# 02/14/2016    sc
#       - converted to postgres for LacZ project
#
# 09/03/3013    lec
#       - TR11350/remove thumbnail
#
# 02/13/2012    lec
#       - TR10978/add x,y,width,heigth
#
# 11/24/2010    lec
#       - TR10033/image class
#
# 05/19/2010    lec
#       - TR10220/updating the Thumbnail key for the Fullsize record
#       - (see TR10161/TRT10159/TR9485 for examples)
#       see bcpFiles...added db.sql() to update the IMG_Image._ThumbnailImage_key
#       after the new fullsize/thumbnail images have been loaded.
#
# 11/01/2006    lec
#       - TR 8002; changes to support bulk loading of thumbnail images
#         and associations between thumbnails and pre-existing full size images.
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
user = os.environ['MGD_DBUSER']
passwordFileName = os.environ['MGD_DBPASSWORDFILE']

mode = os.environ['IMAGELOADMODE']
bcpCommand = os.environ['PG_DBUTILS'] + '/bin/bcpin.csh '
currentDir = os.environ['IMAGELOADDATADIR']
createdBy = os.environ['CREATEDBY']

outCopyrightFileName = os.environ['COPYRIGHTFILE']
outCaptionFileName = os.environ['CAPTIONFILE']

inImageFileName = os.environ['IMAGEFILE']
inPaneFileName = os.environ['IMAGEPANEFILE']

outFileQualifier = os.environ['QUALIFIER_FULLSIZE']

DEBUG = 0               # if 0, not in debug mode
TAB = '\t'              # tab
CRT = '\n'              # carriage return/newline
bcpdelim = TAB          # bcp file delimiter

bcpon = 1               # can the bcp files be bcp-ed into the database?  default is yes.

diagFile = ''           # diagnostic file descriptor
errorFile = ''          # error file descriptor

# input files

inImageFile = ''         # file descriptor
inPaneFile = ''          # file descriptor

# output files

outImageFile = ''       # file descriptor
outCopyrightFile = ''   # file descriptor
outCaptionFile = ''     # file descriptor
outPaneFile = ''        # file descriptor
outAccFile = ''         # file descriptor

imageTable = 'IMG_Image'
paneTable = 'IMG_ImagePane'
accTable = 'ACC_Accession'

# file names 
iFileName = imageTable + '_' + outFileQualifier + '.bcp'
pFileName = paneTable + '_' + outFileQualifier + '.bcp'
aFileName = accTable + '_' + outFileQualifier + '.bcp'

# file names with directory prefix
outImageFileName = currentDir + '/' + iFileName
outPaneFileName = currentDir + '/' + pFileName
outAccFileName = currentDir + '/' + aFileName

diagFileName = ''       # diagnostic file name
errorFileName = ''      # error file name

# primary keys

imageKey = 0            # IMG_Image._Image_key
paneKey = 0             # IMG_ImagePane._ImagePane_key
accKey = 0              # ACC_Accession._Accession_key
mgiKey = 0              # ACC_AccessionMax.maxNumericPart
createdByKey = ''

# accession constants

imageMgiTypeKey = '9'   # Image
imageVocabClassKey = '83'       # Image Class Vocabulary
mgiPrefix = "MGI:"      # Prefix for MGI accession ID
accLogicalDBKey = '1'   # Logical DB Key for MGI accession ID
accPrivate = '0'        # Private status for MGI accession ID (false)
accPreferred = '1'      # Preferred status MGI accession ID (true)
pixPrefix = 'PIX:'      # Prefix for PIX
pixLogicalDBKey = '19'  # Logical DB Key for PIX ID
pixPrivate = '1'        # Private status for PIX ID (true)

FSimageTypeKey = 1072158        # Full Size Image Type key

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
    global bcpCommand
    global diagFile, errorFile, inputFile, errorFileName, diagFileName
    global outImageFile, outPaneFile, outAccFile
    global outCopyrightFile, outCaptionFile
    global inImageFile, inPaneFile
    global createdByKey
 
    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFileName)
 
    bcpCommand = bcpCommand + db.get_sqlServer() + ' ' + db.get_sqlDatabase() + ' %s ' + currentDir + ' %s "\\t" "\\n" mgd'

    diagFileName = currentDir + '/gxdimageload.diagnostics'
    errorFileName = currentDir + '/gxdimageload.error'

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

    db.setTrace(True)

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
#          else, sets global variables
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

    results = db.sql(''' select nextval('img_image_seq') as maxKey ''', 'auto')
    imageKey = results[0]['maxKey']

    results = db.sql(''' select nextval('img_imagepane_seq') as maxKey ''', 'auto')
    paneKey = results[0]['maxKey']

    results = db.sql('''select max(_Accession_key) + 1 as maxKey from ACC_Accession''', 'auto')
    accKey = results[0]['maxKey']

    results = db.sql('''select maxNumericPart + 1 as maxKey from ACC_AccessionMax where prefixPart = '%s' ''' % (mgiPrefix), 'auto')
    mgiKey = results[0]['maxKey']

# Purpose:  BCPs the data into the database
# Returns:  nothing
# Assumes:  nothing
# Effects:  BCPs the data into the database
# Throws:   nothing

def bcpFiles(
   recordsProcessed     # number of records processed (integer)
   ):

    global referenceKey

    if DEBUG or not bcpon:
        return

    outImageFile.close()
    outPaneFile.close()
    outAccFile.close()
    outCopyrightFile.close()
    outCaptionFile.close()

    db.commit()

    bcp1 = bcpCommand % (imageTable, iFileName)
    bcp2 = bcpCommand % (paneTable, pFileName)
    bcp3 = bcpCommand % (accTable, aFileName)

    for bcpCmd in [bcp1, bcp2, bcp3]:
        diagFile.write('%s\n' % bcpCmd)
        os.system(bcpCmd)

    # update the max Accession ID value
    db.sql('''select * from ACC_setMax (%d)''' % (recordsProcessed), None)
    db.commit()

    # update img_image_seq auto-sequence
    db.sql(''' select setval('img_image_seq', (select max(_Image_key) from IMG_Image)) ''', None)
    db.commit()

    # update img_imagepane_seq auto-sequence
    db.sql(''' select setval('img_imagepane_seq', (select max(_ImagePane_key) from IMG_ImagePane)) ''', None)
    db.commit()

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
        tokens = str.split(line[:-1], '\t')

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
            imageInfo = tokens[9]
        except:
            exit(1, 'Invalid Line (%d): %s\n' % (lineNum, line))

        imageClassKey = loadlib.verifyTerm('', imageVocabClassKey, imageClass, lineNum, errorFile)
        if imageClassKey == 0:
            error = 1

        referenceKey = loadlib.verifyReference(jnum, lineNum, errorFile)
        if referenceKey == 0:
            error = 1

        # if errors, continue to next record
        if error:
            continue

        # if no errors, process

        imageTypeKey = FSimageTypeKey

        outImageFile.write(str(imageKey) + TAB + \
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

        if pixID.find('GUDMAP') < 0 and len(pixID) > 0:
            outAccFile.write(str(accKey) + TAB + \
                pixPrefix + str(pixID) + TAB + \
                pixPrefix + TAB + \
                pixID + TAB + \
                pixLogicalDBKey + TAB + \
                str(imageKey) + TAB + \
                imageMgiTypeKey + TAB + \
                pixPrivate + TAB + \
                accPreferred + TAB + \
                str(createdByKey) + TAB + \
                str(createdByKey) + TAB + \
                loaddate + TAB + loaddate + CRT)
    
            accKey = accKey + 1

        if len(imageInfo) > 0:

            imageLogicalDBKey, imageID = imageInfo.split('|')

            outAccFile.write(str(accKey) + TAB + \
                imageID + TAB + \
                imageID + TAB + \
                TAB + \
                imageLogicalDBKey + TAB + \
                str(imageKey) + TAB + \
                imageMgiTypeKey + TAB + \
                accPrivate + TAB + \
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

    #   end of "for line in inImageFile.readlines():"

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
        tokens = str.split(line[:-1], '\t')

        try:
            pixID = tokens[0]
            paneLabel = tokens[1]
            paneWidth = tokens[2]
            paneHeight = tokens[3]
        except:
            exit(1, 'Invalid Line (%d): %s\n' % (lineNum, line))

        paneX = 0
        paneY = 0

        outPaneFile.write(str(paneKey) + TAB + \
            str(imagePix[pixID]) + TAB + \
            mgi_utils.prvalue(paneLabel) + TAB + \
            str(paneX) + TAB + \
            str(paneY) + TAB + \
            str(paneWidth) + TAB + \
            str(paneHeight) + TAB + \
            loaddate + TAB + loaddate + CRT)

        paneKey = paneKey + 1

    #   end of "for line in inPaneFile.readlines():"

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

