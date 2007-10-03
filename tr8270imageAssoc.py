#!/usr/local/bin/python

#
#  tr8270imageAssoc.py
###########################################################################
#
#  Purpose:
#
#      This script will create accession IDs that are associated with the
#      fullsize images. Each accession ID represents the unique portion of
#      the URL that is needed to link the image in MGI to the corresponding
#      page at the Genepaint website. Each ID is formed from numeric values
#      that come from the image file name in the input file.
#
#      Example file name:  MH00000099_0001B.jpg
#                                  |     |
#                         +--------+     |
#                         |              |
#      New accession ID: "99,-Asetstart,A1"
#
#  Usage:
#
#      tr8270imageAssoc.py
#
#  Env Vars:
#
#      MGD_DBUSER
#      MGD_DBPASSWORDFILE
#      IMAGE_LIST_FIG_FILE
#      IMAGE_ACCESSION
#      REFERENCE
#      CREATEDBY
#
#  Inputs:
#
#      ImageListFigLabels.txt - Tab-delimited fields:
#
#          1) Marker MGI ID
#          2) Marker Symbol
#          3) Analysis ID
#          4) Probe ID
#          5) Probe Name
#          6) Specimen ID
#          7) Accession Number
#          8) Set number for image 1
#          9) Slide/section number for image 1
#          10) Image file name for image 1
#          11) Figure label for image 1
#          .
#          .  Repeat image data for a maximum of 24 images.
#          .
#          100) Set number for image 24
#          101) Slide/section number for image 24
#          102) Image file name for image 24
#          103) Figure label for image 24
#
#  Outputs:
#
#      ACC_Accession_Image.bcp
#
#  Exit Codes:
#
#      0:  Successful completion
#      1:  An exception occurred
#
#  Assumes:  Nothing
#
#  Notes:  None
#
###########################################################################
#
#  Modification History:
#
#  Date        SE   Change Description
#  ----------  ---  -------------------------------------------------------
#
#  10/01/2007  DBM  Initial development
#
###########################################################################

import sys
import os
import string
import re
import db
import mgi_utils

#
#  CONSTANTS
#
BCP_DELIM = '\t'

FIRST_IMAGE_FILE_INDEX = 9

FULLSIZE_IMAGE_TYPE_KEY = 1072158

GENEPAINT_LOGICALDB_KEY = '105'
IMAGE_MGITYPE_KEY = '9'
ACC_PRIVATE = '0'
ACC_PREFERRED = '1'
ACC_ID='%s,-Asetstart,-A%s'

#
#  GLOBALS
#
user = os.environ['MGD_DBUSER']
passwordFile = os.environ['MGD_DBPASSWORDFILE']
imageListFile = os.environ['IMAGE_LIST_FIG_FILE']
imageAccFile = os.environ['IMAGE_ACCESSION']
jNumber = os.environ['REFERENCE']
createdBy = os.environ['CREATEDBY']

createdByKey = 0
cdate = mgi_utils.date('%m/%d/%Y')


#
# Purpose: Perform initialization steps.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variables
# Throws: Nothing
#
def init ():
    global createdByKey, accKey

    db.useOneConnection(1)
    db.set_sqlUser(user)
    db.set_sqlPasswordFromFile(passwordFile)

    results = db.sql('select _User_key ' + \
                     'from MGI_User ' + \
                     'where login = "%s"' % (createdBy), 'auto')
    if len(results) > 0:
        createdByKey = results[0]['_User_key']
    else:
        sys.stderr.write('Could not find user: ' + createdBy + '\n')
        sys.exit(1)

    results = db.sql('select max(_Accession_key) + 1 "maxKey" ' + \
                     'from ACC_Accession', 'auto')
    accKey = results[0]['maxKey']

    return


#
# Purpose: Create a dictionary for looking up the image file name for a
#          given figure label.
# Returns: Nothing
# Assumes: Nothing
# Effects: Sets global variable
# Throws: Nothing
#
def buildImageFileLookup ():
    global imageFileLookup

    #
    # Open the input file.
    #
    try:
        fp = open(imageListFile, 'r')
    except:
        sys.stderr.write('Cannot open input file: ' + imageListFile + '\n')
        sys.exit(1)

    #
    # Skip the heading record and process the remaining line of the file.
    #
    imageFileLookup = {}
    line = fp.readline()
    line = fp.readline()
    while line:
        tokens = re.split('\t', line[:-1])
        i = FIRST_IMAGE_FILE_INDEX

        #
        # Check each file name and figure label from the input line.
        #
        while i < len(tokens):
            filename = tokens[i]
            figureLabel = tokens[i+1]

            #
            # If there is no figure label, skip ahead to the next one.
            #
            if figureLabel == '':
                i += 4
                continue

            #
            # Add the filename to the dictionary for the figure label.
            #
            imageFileLookup[figureLabel] = filename
            #print "|" + figureLabel + "| = " + filename
            i += 4

        line = fp.readline()

    return


#
# Purpose: Open the files.
# Returns: Nothing
# Assumes: The names of the files are set in the environment.
# Effects: Sets global variables
# Throws: Nothing
#
def openFiles ():
    global fpImageAccFile

    #
    # Open the output file.
    #
    try:
        fpImageAccFile = open(imageAccFile, 'w')
    except:
        sys.stderr.write('Cannot open output file: ' + imageAccFile + '\n')
        sys.exit(1)

    return


#
# Purpose: Close the files.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def closeFiles ():
    fpImageAccFile.close()

    return


#
# Purpose: Load the bcp file into the database.
# Returns: Nothing
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def runBCP ():

    sys.stdout.flush()

    bcpCmd = 'cat %s | bcp %s..ACC_Accession in %s -c -t"%s" -S%s -U%s' % (passwordFile, db.get_sqlDatabase(), imageAccFile, BCP_DELIM, db.get_sqlServer(), db.get_sqlUser())
    os.system(bcpCmd)

    db.sql('update statistics ACC_Accession', None)

    return


#
# Purpose: Create a bcp file for adding image accession IDs.
# Returns: 0 if successful, 1 for an error
# Assumes: Nothing
# Effects: Nothing
# Throws: Nothing
#
def process ():
    global accKey

    #
    # Get the reference key for the J-Number.
    #
    results = db.sql('select _Object_key ' + \
                     'from ACC_Accession ' + \
                     'where accID = "' + jNumber + '" and ' + \
                           '_LogicalDB_key = 1 and ' + \
                           '_MGIType_key = 1', 'auto')
    refKey = results[0]['_Object_key']

    #
    # Get all the figure labels and image keys for the reference.
    #
    results = db.sql('select figureLabel, _Image_key ' + \
                     'from IMG_Image ' + \
                     'where _Refs_key = ' + str(refKey) + ' and ' + \
                           '_ImageType_key = ' + str(FULLSIZE_IMAGE_TYPE_KEY),
                     'auto')

    for r in results:
        figureLabel = r['figureLabel']
        imageKey = r['_Image_key']

        if imageFileLookup.has_key(figureLabel):
            filename = imageFileLookup[figureLabel]

            #
            # Strip the analysis ID and image number from the file name.  This
            # assumes that the file name follows the pattern:
            #
            #     'MH' + analysisID + '_' + imageNumber + 'B.jpg'
            #
            # where analysisID is 8 characters with 4 or more leading 0's and
            #       imageNumber is 4 characters with 3 or more leading 0's
            #
            analysisID = filename[2:10].lstrip('0')
            imageNumber = filename[11:15].lstrip('0')

            accID = ACC_ID % (analysisID, imageNumber)
            prefixPart = accID
            numericPart = ""

            fpImageAccFile.write(str(accKey) + '\t' +
                                 accID + '\t' +
                                 prefixPart + '\t' +
                                 str(numericPart) + '\t' +
                                 GENEPAINT_LOGICALDB_KEY + '\t' +
                                 str(imageKey) + '\t' +
                                 IMAGE_MGITYPE_KEY + '\t' +
                                 ACC_PRIVATE + '\t' +
                                 ACC_PREFERRED + '\t' +
                                 str(createdByKey) + '\t' +
                                 str(createdByKey) + '\t' +
                                 cdate + '\t' + cdate + '\n')
            accKey += 1

        else:
            print 'Missing image file name for figure label: ' + figureLabel

    return 0


#
# Main
#
init()
buildImageFileLookup()
openFiles()
process()
closeFiles()
runBCP()

sys.exit(0)
